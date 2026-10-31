from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST
)

import time
import logging

from backend.rag_pipeline import get_answer


# ====================================
# Logging
# ====================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)


# ====================================
# FastAPI App
# ====================================

app = FastAPI(
    title="RAG Chatbot API",
    version="1.0"
)


# ====================================
# Prometheus Metrics
# ====================================

RAG_QUERIES = Counter(
    "rag_queries_total",
    "Total RAG chatbot queries"
)

RAG_ERRORS = Counter(
    "rag_query_errors_total",
    "Total RAG chatbot errors"
)

RAG_LATENCY = Histogram(
    "rag_response_latency_seconds",
    "RAG response latency"
)


# ====================================
# Request Model
# ====================================

class QuestionRequest(BaseModel):
    question: str


# ====================================
# Root Endpoint
# ====================================

@app.get("/")
def root():

    return {
        "message": "RAG Chatbot API Running"
    }


# ====================================
# Health Endpoint
# ====================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "rag-chatbot",
        "llm": "llama3"
    }


# ====================================
# Metrics Endpoint
# ====================================

@app.get("/metrics")
def metrics():

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# ====================================
# Ask Endpoint
# ====================================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    start_time = time.time()

    RAG_QUERIES.inc()

    try:

        logger.info(
            f"Question received: {request.question}"
        )

        result = get_answer(
            request.question
        )

        latency = time.time() - start_time

        RAG_LATENCY.observe(
            latency
        )

        return {
            "question": request.question,
            "answer": result["answer"],
            "sources": result["sources"],
            "latency_seconds": round(
                latency,
                2
            )
        }

    except Exception as e:

        RAG_ERRORS.inc()

        logger.error(
            f"RAG Error: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
