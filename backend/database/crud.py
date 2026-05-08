import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.database import models

logger = logging.getLogger(__name__)

# --- User Operations ---

def create_user(db: Session, email: str):
    """Create a new user or return existing if email already exists."""
    try:
        existing_user = db.query(models.User).filter(models.User.email == email).first()
        if existing_user:
            return existing_user

        db_user = models.User(email=email)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating user {email}: {str(e)}")
        raise

# --- Chat Session Operations ---

def create_chat_session(db: Session, user_id: int, title: str = "New Chat"):
    """Create a new conversation thread linked to a specific user."""
    try:
        db_session = models.ChatSession(user_id=user_id, title=title)
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating chat session for user {user_id}: {str(e)}")
        raise

def get_chat_session(db: Session, session_id: int):
    """Retrieve a single chat session by its ID."""
    try:
        return db.query(models.ChatSession)\
                 .filter(models.ChatSession.id == session_id)\
                 .first()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving chat session {session_id}: {str(e)}")
        raise

# --- Message Operations ---

def save_message(db: Session, session_id: int, role: str, content: str):
    """Save a single raw message (user or ai) into a session history."""
    try:
        db_message = models.Message(
            session_id=session_id,
            role=role,
            content=content
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error saving {role} message to session {session_id}: {str(e)}")
        raise

def get_chat_history(db: Session, session_id: int, limit: int = 50):
    """Retrieve chronologically ordered chat history for LLM context."""
    try:
        return db.query(models.Message)\
                 .filter(models.Message.session_id == session_id)\
                 .order_by(models.Message.timestamp.asc())\
                 .limit(limit)\
                 .all()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving chat history for session {session_id}: {str(e)}")
        raise

def get_user_recent_messages(db: Session, user_id: int, exclude_session_id: int = None, limit: int = 10):
    """
    Retrieve the most recent messages across ALL of a user's sessions.
    Used to provide cross-session conversational continuity.
    """
    try:
        # Get all session IDs belonging to this user
        sessions = db.query(models.ChatSession)\
                     .filter(models.ChatSession.user_id == user_id)\
                     .all()
        session_ids = [s.id for s in sessions if s.id != exclude_session_id]

        if not session_ids:
            return []

        # Fetch most recent messages across those sessions, ordered by time
        return db.query(models.Message)\
                 .filter(models.Message.session_id.in_(session_ids))\
                 .order_by(models.Message.timestamp.desc())\
                 .limit(limit)\
                 .all()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving cross-session history for user {user_id}: {str(e)}")
        return []

# --- User Memory Operations ---

def save_user_memory(db: Session, user_id: int, memory_type: str, content: str):
    """Extract and save a long-term fact or preference for a user."""
    try:
        db_memory = models.UserMemory(
            user_id=user_id,
            memory_type=memory_type,
            content=content
        )
        db.add(db_memory)
        db.commit()
        db.refresh(db_memory)
        return db_memory
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error saving memory for user {user_id}: {str(e)}")
        raise

def get_user_memories(db: Session, user_id: int, memory_type: str = None):
    """Retrieve long-term memory chunks to inject into the LLM system prompt."""
    try:
        query = db.query(models.UserMemory).filter(models.UserMemory.user_id == user_id)
        if memory_type:
            query = query.filter(models.UserMemory.memory_type == memory_type)
        return query.order_by(models.UserMemory.created_at.desc()).all()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving memories for user {user_id}: {str(e)}")
        raise
