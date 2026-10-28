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


app = FastAPI(
    title="Enterprise RAG Chatbot",
    version="1.0.0"
)


rag_requests_total = Counter(
    "rag_requests_total",
    "Total chatbot requests"
)

rag_response_time_seconds = Histogram(
    "rag_response_time_seconds",
    "RAG response latency"
)


print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Loading ChromaDB...")

db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

print("Loading Llama3...")

llm = ChatOllama(
    model="llama3"
)


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def root():

    return {
        "message": "Enterprise RAG Chatbot API",
        "docs": "/docs"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "rag-chatbot",
        "llm": "llama3"
    }


@app.get("/metrics")
def metrics():

    return Response(
        generate_latest(),
        media_type="text/plain"
    )


@app.post("/ask")
def ask_question(request: QuestionRequest):

    start_time = time.time()

    rag_requests_total.inc()

    docs = db.similarity_search(
        request.question,
        k=3
    )

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    sources = list(
        {
            doc.metadata.get(
                "source",
                "Unknown"
            )
            for doc in docs
        }
    )

    prompt = f"""
You are an expert AWS, Kubernetes,
Docker and DevOps assistant.

Answer ONLY from the provided context.

Context:
{context}

Question:
{request.question}
"""

    answer = llm.invoke(
        prompt
    )

    rag_response_time_seconds.observe(
        time.time() - start_time
    )

    return {
        "question": request.question,
        "answer": answer.content,
        "sources": sources
    }
