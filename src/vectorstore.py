from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load existing ChromaDB
db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

print("=" * 80)
print("Enterprise RAG Knowledge Base")
print("=" * 80)

while True:

    query = input(
        "\nAsk a question (or type 'exit'): "
    )

    if query.lower() == "exit":
        print("\nGoodbye!")
        break

    results = db.similarity_search(
        query,
        k=3
    )

    print("\nTop Matching Chunks:\n")

    for i, result in enumerate(
        results,
        start=1
    ):

        print("=" * 80)

        source = result.metadata.get(
            "source",
            "Unknown Source"
        )

        page = result.metadata.get(
            "page",
            "N/A"
        )

        print(
            f"Chunk {i}"
        )

        print(
            f"Source : {source}"
        )

        print(
            f"Page   : {page}"
        )

        print("=" * 80)

        print(
            result.page_content[:1000]
        )

        print("\n")

