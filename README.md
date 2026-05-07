# SWS AI RAG Chatbot

An AI-powered Retrieval-Augmented Generation (RAG) chatbot for answering employee questions from internal company policy documents. Built with FastAPI, LangChain, FAISS, and Google Gemini 2.5 Flash.

## 🚀 Features

- **Automated PDF Ingestion**: Parses company policy PDFs locally and intelligently chunks text.
- **Local Vector Database**: Generates highly accurate embeddings and stores them locally using FAISS.
- **Conversational Memory**: Remembers chat history for contextual follow-up questions.
- **Source Citation**: Returns the exact source documents used to formulate every answer.
- **REST API**: Production-ready FastAPI endpoints for integration with any frontend UI.

## 🛠️ Architecture

- **Backend Framework**: FastAPI
- **AI/LLM Orchestration**: LangChain (v0.2.x stable)
- **Generative Model**: Google Gemini 2.5 Flash via `langchain-google-genai`
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Store**: FAISS (CPU)
- **Document Loading**: PyMuPDF

## 📦 Setup & Installation

### 1. Prerequisites
- Python 3.10+
- A Google Gemini API Key

### 2. Installation
Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/Rethankumar-cv/sws-ai-rag-chatbot.git
cd sws-ai-rag-chatbot
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory and add your Google API key:
```env
GOOGLE_API_KEY="your_actual_api_key_here"
```

## ⚙️ Usage

### 1. Ingest Documents
Place your company policy PDFs into `data/pdfs/`. Then, run the ingestion script to generate the FAISS vector index:

```bash
python -m backend.ingest
```

### 2. Start the API Server
Launch the FastAPI backend server using Uvicorn:

```bash
uvicorn backend.app:app --reload
```

### 3. Test the Endpoints
Once running, visit the interactive Swagger UI at:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

You can send POST requests to `/chat` with a JSON body:
```json
{
  "query": "What is the company leave policy?"
}
```

## 📂 Project Structure

```text
sws-ai-rag-chatbot/
│
├── backend/
│   ├── __init__.py
│   ├── app.py              # FastAPI server and endpoints
│   ├── config.py           # Centralized application configurations
│   ├── ingest.py           # PDF loader, chunker, and FAISS vector builder
│   └── rag_pipeline.py     # Gemini Conversational Chain and Retriever
│
├── data/
│   └── pdfs/               # Raw PDF documents
│
├── frontend/
│   ├── __init__.py
│   └── streamlit_app.py    # (Upcoming) Streamlit chat interface
│
├── vector_store/           # Generated FAISS database
├── .env                    # Environment variables
├── .gitignore              
├── requirements.txt        # Pinned Python dependencies
└── README.md
```
