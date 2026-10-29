import os
import time

from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel

from prometheus_client import (
    Counter,
    Histogram,
    generate_latest
)

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama

# -----------------------------------------------------
# FastAPI App
# -----------------------------------------------------

app = FastAPI(
    title="Enterprise RAG Chatbot",
    description="RAG Chatbot using ChromaDB and Ollama",
    version="1.0.0"
)

# -----------------------------------------------------
# Metrics
# -----------------------------------------------------

rag_requests_total = Counter(
    "rag_requests_total",
    "Total RAG requests"
)

rag_response_time_seconds = Histogram(
    "rag_response_time_seconds",
    "RAG response latency"
)

# -----------------------------------------------------
# Ollama Configuration
# -----------------------------------------------------

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

print(
    f"Using Ollama URL: {OLLAMA_BASE_URL}"
)

# -----------------------------------------------------
# Embeddings
# -----------------------------------------------------

print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -----------------------------------------------------
# ChromaDB
# -----------------------------------------------------

print("Loading vector database...")

db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

# -----------------------------------------------------
# Ollama
# -----------------------------------------------------

print("Loading Llama3...")

llm = ChatOllama(
    model="llama3",
    base_url=OLLAMA_BASE_URL,
    temperature=0
)

# -----------------------------------------------------
# Request Model
# -----------------------------------------------------

class QuestionRequest(BaseModel):
    question: str

# -----------------------------------------------------
# Root Endpoint
# -----------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "Enterprise RAG Chatbot API",
        "docs": "/docs"
    }

# -----------------------------------------------------
# Health Endpoint
# -----------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "rag-chatbot",
        "llm": "llama3",
        "ollama_url": OLLAMA_BASE_URL
    }

# -----------------------------------------------------
# Metrics Endpoint
# -----------------------------------------------------

@app.get("/metrics")
def metrics():

    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )

# -----------------------------------------------------
# Ask Endpoint
# -----------------------------------------------------

@app.post("/ask")
def ask_question(request: QuestionRequest):

    start_time = time.time()

    rag_requests_total.inc()

    try:

        docs = db.similarity_search(
            request.question,
            k=3
        )

        context = "\n\n".join(
            doc.page_content
            for doc in docs
        )

        sources = list({
            doc.metadata.get(
                "source",
                "Unknown"
            )
            for doc in docs
        })

        prompt = f"""
You are an expert AWS, Kubernetes,
Docker and DevOps assistant.

Use ONLY the provided context.

If the answer is not present
in the context, respond with:

"I could not find this information in the indexed documents."

Context:
{context}

Question:
{request.question}

Answer:
"""

        response = llm.invoke(
            prompt
        )

        rag_response_time_seconds.observe(
            time.time() - start_time
        )

        return {
            "question": request.question,
            "answer": response.content,
            "sources": sources
        }

    except Exception as e:

        return {
            "question": request.question,
            "error": str(e)
        }

# -----------------------------------------------------
# Local Run
# -----------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
