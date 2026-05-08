import logging
import os
import jwt
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from backend.rag_pipeline import RAGPipeline
from backend.database.connection import engine, Base, get_db
from backend.database import crud, models
from backend.memory_extractor import MemoryExtractor
from backend.auth import get_current_user

load_dotenv()

# Automatically create database tables if they don't exist
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="SWS AI RAG Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipelines on startup
try:
    rag_pipeline = RAGPipeline()
    memory_extractor = MemoryExtractor()
except Exception as e:
    logger.error(f"Failed to initialize AI pipelines: {str(e)}")
    rag_pipeline = None
    memory_extractor = None

# --- Schemas ---

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    timestamp: str

class ConversationResponse(BaseModel):
    id: int
    title: str
    updated_at: str
    messages: Optional[List[MessageResponse]] = []

class QueryRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    temperature: Optional[float] = 0.7
    top_k: Optional[int] = 5

class QueryResponse(BaseModel):
    response: str
    conversation_id: int
    sources: List[str]

class DocumentResponse(BaseModel):
    id: int
    filename: str
    upload_date: str
    status: str
    size: Optional[int]

# --- Auth Endpoints ---

@app.post("/auth/login", response_model=AuthResponse)
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # In a real app, verify password against DB. 
    # For this demo, we'll auto-create/get user by email-like username.
    email = f"{username}@sws.ai" if "@" not in username else username
    user = crud.create_user(db, email=email)
    
    # Sign JWT token
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    secret = os.getenv("SUPABASE_JWT_SECRET", "secret")
    token = jwt.encode(payload, secret, algorithm="HS256")
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": username
        }
    }

@app.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == current_user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "email": user.email,
        "username": user.email.split("@")[0]
    }

# --- Chat Endpoints ---

@app.get("/chat/history", response_model=List[ConversationResponse])
async def get_chat_history(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == current_user["email"]).first()
    sessions = db.query(models.ChatSession).filter(models.ChatSession.user_id == user.id).all()
    return [
        {
            "id": s.id,
            "title": s.title,
            "updated_at": s.created_at.isoformat(),
        } for s in sessions
    ]

@app.get("/chat/{session_id}", response_model=ConversationResponse)
async def get_chat_details(session_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == current_user["email"]).first()
    session = crud.get_chat_session(db, session_id=session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    messages = crud.get_chat_history(db, session_id=session_id)
    return {
        "id": session.id,
        "title": session.title,
        "updated_at": session.created_at.isoformat(),
        "messages": [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp.isoformat()
            } for m in messages
        ]
    }

@app.post("/chat", response_model=QueryResponse)
async def chat(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not rag_pipeline:
        raise HTTPException(status_code=500, detail="AI pipeline not initialized")

    user = db.query(models.User).filter(models.User.email == current_user["email"]).first()
    
    session_id = request.conversation_id
    if not session_id:
        title = request.message[:50]
        session = crud.create_chat_session(db, user_id=user.id, title=title)
        session_id = session.id
    
    # Update pipeline with dynamic settings if needed (RAGPipeline would need to support these)
    # For now we use the existing query method
    result = rag_pipeline.query(request.message, session_id=session_id, user_id=user.id, db=db)
    
    if memory_extractor:
        background_tasks.add_task(
            memory_extractor.extract_and_save,
            db=db,
            user_id=user.id,
            user_message=request.message,
            ai_response=result["answer"]
        )

    return {
        "response": result["answer"],
        "conversation_id": session_id,
        "sources": result["sources"]
    }

# --- Document Endpoints ---

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == current_user["email"]).first()
    
    # Save file record to DB
    doc = models.Document(
        user_id=user.id,
        filename=file.filename,
        file_path=f"data/{file.filename}",
        status="ready",
        size=0 # Should be calculated
    )
    db.add(doc)
    db.commit()
    
    # In a real app, save the file to disk/S3 and trigger ingestion
    # For now, we just mock the success
    return {"message": "File uploaded successfully"}

@app.get("/documents", response_model=List[DocumentResponse])
async def list_documents(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == current_user["email"]).first()
    docs = db.query(models.Document).filter(models.Document.user_id == user.id).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "upload_date": d.upload_date.isoformat(),
            "status": d.status,
            "size": d.size
        } for d in docs
    ]

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == current_user["email"]).first()
    doc = db.query(models.Document).filter(models.Document.id == doc_id, models.Document.user_id == user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted"}

@app.get("/health")
async def health_check():
    return {"status": "healthy" if rag_pipeline else "degraded"}
