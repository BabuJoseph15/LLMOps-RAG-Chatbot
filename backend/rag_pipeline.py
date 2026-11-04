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

    # Retrieve fewer but higher quality chunks
    docs = db.max_marginal_relevance_search(
        question,
        k=3,
        fetch_k=10
    )

    if not docs:
        return {
            "answer": "No relevant information found.",
            "sources": []
        }

    # Limit context size
    context = "\n\n".join(
        [doc.page_content[:500] for doc in docs]
    )

    # Debug output
    print("=" * 80)
    print("RETRIEVED CONTEXT")
    print("=" * 80)

    for doc in docs:
        print(doc.page_content[:1000])
        print("-" * 80)

    prompt = f"""
You are a helpful AI assistant.

Answer ONLY using the supplied context.

If the answer exists in the context,
provide a clear and concise answer.

If the answer is not available,
respond exactly with:

"I could not find the answer in the provided documents."

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

        if source not in sources:
            sources.append(source)

    return {
        "answer": answer,
        "sources": sources
    }
