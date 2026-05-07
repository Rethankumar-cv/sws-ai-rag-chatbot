import os
import logging
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

from backend.config import FAISS_INDEX_PATH, EMBEDDING_MODEL, RETRIEVAL_K

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
                model="gemini-2.5-flash", 
                temperature=0.3,
                google_api_key=api_key
            )
            
            # Setup Memory
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
            
            # Setup Chain
            self.chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.retriever,
                memory=self.memory,
                return_source_documents=True
            )
            logger.info("RAG pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing RAG pipeline: {str(e)}")
            raise

    def query(self, question: str):
        try:
            response = self.chain.invoke({"question": question})
            answer = response["answer"]
            source_docs = response.get("source_documents", [])
            sources = list(set([doc.metadata.get("source", "Unknown") for doc in source_docs]))
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
