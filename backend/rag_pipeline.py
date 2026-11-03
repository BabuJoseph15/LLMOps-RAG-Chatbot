from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_PATH = "chroma_db"

# Embedding Model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Ollama Connection
llm = OllamaLLM(
    model="llama3",
    base_url="http://host.minikube.internal:11434"
)


def get_answer(question: str):

    # Load Chroma Vector Store
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_model
    )

    # Better retrieval using MMR
    docs = db.max_marginal_relevance_search(
        question,
        k=6,
        fetch_k=20
    )

    # Remove noise
    filtered_docs = []

    for doc in docs:

        content = doc.page_content.strip()

        if not content:
            continue

        lower_content = content.lower()

        # Skip cover pages and contents
        if "contents" in lower_content:
            continue

        if (
            "chapter" in lower_content
            and len(content) < 150
        ):
            continue

        filtered_docs.append(doc)

    docs = filtered_docs[:5]

    if not docs:

        return {
            "answer": "No relevant information found.",
            "sources": []
        }

    # Build Context
    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = f"""
You are an expert AI assistant.

Answer ONLY using the provided context.

If the answer is not available in the context,
respond:

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

        sources.append(source)

    return {
        "answer": answer,
        "sources": list(set(sources))
    }
