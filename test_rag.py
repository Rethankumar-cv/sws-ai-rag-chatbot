import os
import sys
from dotenv import load_dotenv

# Ensure we are in the correct directory
os.chdir(r"e:\SWS-AI\sws-ai-rag-chatbot")
sys.path.append(os.getcwd())

load_dotenv()

try:
    from backend.rag_pipeline import RAGPipeline
    from backend.database.database import SessionLocal
    
    print("Initializing RAG Pipeline...")
    rag = RAGPipeline()
    db = SessionLocal()
    
    print("Sending test query...")
    # Mocking user_id=1, session_id=1
    result = rag.query("Tell me about SWS AI and its mission.", session_id=1, user_id=1, db=db)
    
    print("\n--- RESPONSE ---")
    print(result['answer'])
    print("\n--- SOURCES ---")
    print(result['sources'])
    
except Exception as e:
    print(f"\n[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
