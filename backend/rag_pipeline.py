import os
import logging
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from sqlalchemy.orm import Session
from backend.database import crud

from backend.config import FAISS_INDEX_PATH, USER_MEMORY_FAISS_PATH, EMBEDDING_MODEL, RETRIEVAL_K

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        logger.info("Loading vector database...")
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
            self.vector_store = FAISS.load_local(
                FAISS_INDEX_PATH, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": RETRIEVAL_K})
            
            # Setup LLM
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                logger.error("GOOGLE_API_KEY not found in environment variables.")
                raise ValueError("Missing GOOGLE_API_KEY")
                
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-pro", 
                temperature=0.3,
                google_api_key=api_key
            )
            
            # Chain is removed. We will build custom optimized prompts manually.
            logger.info("RAG pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing RAG pipeline: {str(e)}")
            raise

    def query(self, question: str, session_id: int, user_id: int, db: Session):
        try:
            # 1. Fetch Semantic User Memory dynamically using FAISS similarity search
            user_memories = []
            if os.path.exists(USER_MEMORY_FAISS_PATH):
                try:
                    memory_store = FAISS.load_local(
                        USER_MEMORY_FAISS_PATH, 
                        self.embeddings, 
                        allow_dangerous_deserialization=True
                    )
                    # Search specifically for memories relevant to the current question, locked to this user
                    docs = memory_store.similarity_search(
                        question, 
                        k=10, 
                        filter={"user_id": user_id}
                    )
                    # Security filter: guarantee no cross-tenant memory leakage
                    user_memories = [doc for doc in docs if doc.metadata.get("user_id") == user_id][:3]
                except Exception as e:
                    logger.warning(f"Could not load semantic memory index: {e}")
            # 2. Fetch Company Document Context
            company_docs = self.retriever.invoke(question)
            
            # Deduplicate company context to save tokens
            unique_company_docs = []
            seen_content = set()
            for doc in company_docs:
                if doc.page_content not in seen_content:
                    unique_company_docs.append(doc)
                    seen_content.add(doc.page_content)

            system_prompt = "You are a highly intelligent corporate AI assistant for SWS AI.\n\n"

            # Inject cross-session history (previous conversations this user had)
            past_messages = crud.get_user_recent_messages(
                db, user_id=user_id, exclude_session_id=session_id, limit=10
            )
            if past_messages:
                # Reverse to get chronological order (they came back desc)
                past_messages = list(reversed(past_messages))
                system_prompt += "=== PREVIOUS CONVERSATION HISTORY ===\n"
                system_prompt += "The user has spoken with you before. Here are their most recent past messages for context:\n"
                for m in past_messages:
                    role_label = "User" if m.role == "user" else "Assistant"
                    system_prompt += f"{role_label}: {m.content}\n"
                system_prompt += "\n"

            if user_memories:
                system_prompt += "=== PERSONALIZED USER MEMORIES ===\n"
                system_prompt += "Long-term facts extracted from this user's past conversations:\n"
                for m in user_memories:
                    system_prompt += f"- {m.metadata.get('memory_type', 'FACT').upper()}: {m.page_content}\n"
                system_prompt += "\n"

            if unique_company_docs:
                system_prompt += "=== COMPANY POLICY CONTEXT ===\n"
                system_prompt += "Use this official documentation to answer factual questions:\n"
                for doc in unique_company_docs:
                    system_prompt += f"- {doc.page_content}\n"
                system_prompt += "\n"

            system_prompt += "INSTRUCTIONS:\n"
            system_prompt += "1. Use PREVIOUS CONVERSATION HISTORY to maintain continuity across sessions.\n"
            system_prompt += "2. Prioritize PERSONALIZED USER MEMORIES for personal preferences and context.\n"
            system_prompt += "3. Use COMPANY POLICY CONTEXT for factual policy questions.\n"
            system_prompt += "4. If the user asks about a previous conversation, summarize from PREVIOUS CONVERSATION HISTORY.\n"
            system_prompt += "5. Respond naturally — never reveal you are reading from 'contexts' or 'memory'.\n"

            messages = [SystemMessage(content=system_prompt)]

            # 4. Rebuild history from PostgreSQL
            raw_history = crud.get_chat_history(db, session_id=session_id, limit=20)
            for msg in raw_history:
                if msg.role == 'user':
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == 'ai':
                    messages.append(AIMessage(content=msg.content))
            
            # Append current question
            messages.append(HumanMessage(content=question))

            # 5. Query Gemini
            response = self.llm.invoke(messages)
            answer = response.content
            
            # 6. Save new messages directly to DB
            crud.save_message(db, session_id=session_id, role="user", content=question)
            crud.save_message(db, session_id=session_id, role="ai", content=answer)
            
            # Extract Sources
            sources = list(set([doc.metadata.get("source", "Unknown") for doc in unique_company_docs]))
            
            return {
                "answer": answer,
                "sources": sources
            }
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "answer": "I'm sorry, I encountered an error while processing your request.",
                "sources": []
            }
