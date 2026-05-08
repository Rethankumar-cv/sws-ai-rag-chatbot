import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

# Provide a local SQLite fallback if Supabase PostgreSQL isn't configured yet
if not DATABASE_URL:
    logger.warning("DATABASE_URL is not set! Falling back to local SQLite database for development.")
    DATABASE_URL = "sqlite:///./rag_database.db"
    
# SQLite specific configuration
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# pool_pre_ping=True helps handle dropped connections safely (important for cloud DBs like Supabase)
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True if not DATABASE_URL.startswith("sqlite") else False,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency generator for FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
