from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_PATH = "chroma_db"

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

llm = OllamaLLM(
    model="llama3"
)


def get_answer(question: str):

    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_model
    )

    docs = db.similarity_search(
        question,
        k=3
    )

    if not docs:

        return {
            "answer": "No relevant information found.",
            "sources": []
        }

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = f"""
You are a helpful AI assistant.

Answer ONLY using the context.

If the answer is not found,
say:

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
