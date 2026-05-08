import os
import re
import json
import logging
from threading import Lock
from datetime import datetime, timezone
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from sqlalchemy.orm import Session
from backend.database import crud
from backend.config import USER_MEMORY_FAISS_PATH, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

# Global lock to prevent race conditions when multiple tasks write to FAISS
faiss_lock = Lock()

VALID_TYPES = ['preferences', 'professional background', 'ongoing tasks', 'personal context']

class MemoryExtractor:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        # Plain LLM — no structured output wrapper (avoids Gemini JSON Schema bug)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.0,
            google_api_key=api_key
        )
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

        self.prompt = PromptTemplate(
            template="""You are a memory extraction AI. Analyze the conversation and extract important long-term facts about the USER only.

Valid memory_type values: preferences | professional background | ongoing tasks | personal context

Rules:
- Only extract facts explicitly stated or clearly implied by the USER.
- Ignore greetings, generic questions, and irrelevant chat noise.
- Keep content concise (1-2 sentences max).
- If nothing is worth remembering, return an empty list.

Return ONLY a valid JSON array (no markdown, no explanation):
[
  {{"memory_type": "preferences", "content": "..."}},
  {{"memory_type": "ongoing tasks", "content": "..."}}
]

Conversation:
User: {user_message}
AI: {ai_response}

JSON array:""",
            input_variables=["user_message", "ai_response"]
        )

    def _parse_memories(self, raw_text: str):
        """Robustly parse JSON array from LLM response."""
        try:
            # Strip markdown code fences if present
            cleaned = re.sub(r"```(?:json)?", "", raw_text).strip().rstrip("```").strip()
            # Find the first JSON array in the text
            match = re.search(r'\[.*\]', cleaned, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            logger.warning(f"Memory parse error: {e} | Raw: {raw_text[:200]}")
        return []

    def _save_to_faiss(self, user_id: int, memory_type: str, content: str):
        metadata = {
            "user_id": user_id,
            "memory_type": memory_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        with faiss_lock:
            try:
                if os.path.exists(USER_MEMORY_FAISS_PATH):
                    store = FAISS.load_local(
                        USER_MEMORY_FAISS_PATH,
                        self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                    store.add_texts(texts=[content], metadatas=[metadata])
                else:
                    store = FAISS.from_texts(texts=[content], embedding=self.embeddings, metadatas=[metadata])
                store.save_local(USER_MEMORY_FAISS_PATH)
            except Exception as e:
                logger.error(f"Failed to save memory to FAISS: {e}")

    def extract_and_save(self, db: Session, user_id: int, user_message: str, ai_response: str):
        """Analyze a message pair and persist any semantic memories."""
        try:
            chain = self.prompt | self.llm
            result = chain.invoke({"user_message": user_message, "ai_response": ai_response})
            raw_text = result.content if hasattr(result, "content") else str(result)

            memories = self._parse_memories(raw_text)

            for mem in memories:
                memory_type = str(mem.get("memory_type", "")).lower().strip()
                content = str(mem.get("content", "")).strip()

                if memory_type in VALID_TYPES and content:
                    # 1. Save to PostgreSQL
                    crud.save_user_memory(db=db, user_id=user_id, memory_type=memory_type, content=content)
                    # 2. Vectorize and save to FAISS
                    self._save_to_faiss(user_id=user_id, memory_type=memory_type, content=content)
                    logger.info(f"Memory saved [{memory_type}] for user {user_id}: {content}")

        except Exception as e:
            logger.error(f"Memory extraction failed: {e}")
