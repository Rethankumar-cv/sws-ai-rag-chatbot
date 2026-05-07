import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.rag_pipeline import RAGPipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="SWS AI RAG Chatbot")

# Initialize pipeline on startup
try:
    rag_pipeline = RAGPipeline()
except Exception as e:
    logger.error(f"Failed to initialize RAG pipeline: {str(e)}")
    rag_pipeline = None

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]

@app.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    if not rag_pipeline:
        raise HTTPException(status_code=500, detail="RAG pipeline is not initialized (FAISS index might be missing). Please run ingest.py first.")
    
    response = rag_pipeline.query(request.query)
    return QueryResponse(
        answer=response["answer"],
        sources=response["sources"]
    )

@app.get("/health")
async def health_check():
    status = "healthy" if rag_pipeline else "unhealthy"
    return {"status": status}
