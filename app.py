from fastapi import FastAPI
from pydantic import BaseModel

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama


app = FastAPI(
    title="Enterprise RAG Chatbot",
    description="LLMOps RAG Chatbot powered by ChromaDB and Llama3",
    version="1.0.0"
)


print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Loading vector database...")

db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

print("Loading Llama3...")

llm = ChatOllama(
    model="llama3",
    temperature=0
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


@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question

    docs = db.similarity_search(
        question,
        k=3
    )

    sources = []

    context_parts = []

    for doc in docs:

        source = doc.metadata.get(
            "source",
            "Unknown"
        )

        if source not in sources:
            sources.append(source)

        context_parts.append(
            doc.page_content
        )

    context = "\n\n".join(
        context_parts
    )

    prompt = f"""
You are an expert AWS, Kubernetes,
Docker and DevOps assistant.

Answer ONLY from the provided context.

If the answer cannot be found,
respond with:

"I could not find this information
in the indexed documents."

Context:
{context}

Question:
{question}

Answer:
"""

    response = llm.invoke(
        prompt
    )

    return {
        "question": question,
        "answer": response.content,
        "sources": sources
    }
