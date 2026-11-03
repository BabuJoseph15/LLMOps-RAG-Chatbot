from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_PATH = "chroma_db"

# Embedding Model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Ollama LLM
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

    # Retrieve Documents
    docs = db.similarity_search(
        question,
        k=3
    )

    if not docs:

        return {
            "answer": "No relevant information found.",
            "sources": []
        }

    # Create Context
    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = f"""
You are a helpful AI Assistant.

Answer ONLY using the provided context.

If the answer is not available in the context,
respond with:

"I could not find the answer in the provided documents."

Context:
{context}

Question:
{question}

Answer:
"""

    # Generate Response
    answer = llm.invoke(prompt)

    sources = []

    for doc in docs:

        if doc.metadata:

            source = doc.metadata.get(
                "source",
                "unknown"
            )

            sources.append(source)

    return {
        "answer": answer,
        "sources": list(set(sources))
    }
