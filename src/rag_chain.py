from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from langchain_ollama import ChatOllama


print("\nLoading Embedding Model...")

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
    model="llama3",
    temperature=0
)

print("\n" + "=" * 80)
print("Enterprise DevOps / Cloud RAG Chatbot")
print("=" * 80)


while True:

    question = input(
        "\nAsk a question (type 'exit' to quit): "
    )

    if question.lower() in ["exit", "quit"]:

        print("\nGoodbye!")
        break

    print("\nSearching knowledge base...")

    docs = db.similarity_search(
        question,
        k=3
    )

    print("\nRetrieved Sources:")

    context_parts = []

    for doc in docs:

        source = doc.metadata.get(
            "source",
            "Unknown"
        )

        page = doc.metadata.get(
            "page",
            "N/A"
        )

        print(
            f" - {source} "
            f"(Page {page})"
        )

        context_parts.append(
            doc.page_content
        )

    context = "\n\n".join(
        context_parts
    )

    prompt = f"""
You are an expert Cloud, DevOps, Kubernetes,
Docker and AWS assistant.

Answer ONLY using the supplied context.

If the answer is not present in the context,
say:

"I could not find this information in the indexed documents."

Context:
{context}

Question:
{question}

Answer:
"""

    print("\nGenerating answer...\n")

    response = llm.invoke(
        prompt
    )

    print("=" * 80)
    print("ANSWER")
    print("=" * 80)

    print(response.content)

    print("\n")
