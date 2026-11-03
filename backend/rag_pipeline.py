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
# Ollama Model
# ==================================================

llm = OllamaLLM(
    model="llama3",
    base_url="http://host.minikube.internal:11434"
)

# ==================================================
# RAG Function
# ==================================================

def get_answer(question: str):

    db = Chroma(
        collection_name="langchain",
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_model
    )

    # Better retrieval
    docs = db.max_marginal_relevance_search(
        question,
        k=6,
        fetch_k=20
    )

    if not docs:
        return {
            "answer": "No relevant information found.",
            "sources": []
        }

    # Build context directly from retrieved chunks
    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = f"""
You are a helpful AI assistant.

Use ONLY the supplied context.

If the answer exists in the context,
answer the question clearly.

If the answer is not available,
respond:

I could not find the answer in the provided documents.

Context:
{context}

Question:
{question}

Answer:
"""

    answer = llm.invoke(prompt)

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
