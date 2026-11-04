from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_PATH = "chroma_db"

# ==================================================
# Embedding Model
# ==================================================

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ==================================================
# Ollama LLM
# ==================================================

llm = OllamaLLM(
    model="llama3",
    base_url="http://host.minikube.internal:11434"
)

# ==================================================
# RAG Function
# ==================================================

def get_answer(question: str):

    # Connect to ChromaDB
    db = Chroma(
        collection_name="langchain",
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_model
    )

    # Better retrieval using MMR
    docs = db.max_marginal_relevance_search(
        question,
        k=10,
        fetch_k=50
    )

    if not docs:
        return {
            "answer": "No relevant information found.",
            "sources": []
        }

    # Build context
    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    # Prompt
    prompt = f"""
You are a Kubernetes, Docker and Cloud Computing expert.

Use ONLY the supplied context to answer.

If the answer exists in the context,
provide a clear and detailed answer.

If the answer is not available,
respond exactly with:

"I could not find the answer in the provided documents."

Context:
{context}

Question:
{question}

Answer:
"""

    # Generate answer
    answer = llm.invoke(prompt)

    # Extract sources
    sources = []

    for doc in docs:

        source = doc.metadata.get(
            "source",
            "unknown"
        )

        sources.append(source)

    return {
        "answer": answer,
        "sources": list(set(sources))
    }
