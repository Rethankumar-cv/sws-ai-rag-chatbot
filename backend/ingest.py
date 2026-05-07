import os
import logging
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from backend.config import (
    PDF_DIR, 
    FAISS_INDEX_PATH, 
    CHUNK_SIZE, 
    CHUNK_OVERLAP, 
    EMBEDDING_MODEL
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_documents(pdf_dir: str):
    logger.info(f"Loading PDF documents...")
    documents = []
    if not os.path.exists(pdf_dir):
        logger.warning(f"Directory {pdf_dir} does not exist.")
        return documents
        
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(pdf_dir, filename)
            loader = PyMuPDFLoader(file_path)
            docs = loader.load()
            # Add metadata
            for doc in docs:
                doc.metadata["source"] = filename
            documents.extend(docs)
    logger.info(f"Total PDFs loaded: {len(documents)}")
    return documents

def split_documents(documents):
    logger.info("Splitting documents...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"Total chunks created: {len(chunks)}")
    return chunks

def create_vector_store(chunks, index_path: str):
    logger.info("Creating embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    try:
        vector_store = FAISS.from_documents(chunks, embeddings)
        logger.info("Saving FAISS index...")
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        vector_store.save_local(index_path)
        logger.info("FAISS index saved successfully")
    except Exception as e:
        logger.error(f"Error creating/saving FAISS index: {str(e)}")
        raise

if __name__ == "__main__":
    docs = load_documents(PDF_DIR)
    if docs:
        chunks = split_documents(docs)
        create_vector_store(chunks, FAISS_INDEX_PATH)
    else:
        logger.warning("No documents to process.")
