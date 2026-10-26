import os
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


DATA_DIR = "data"
CHROMA_DIR = "chroma_db"


def load_and_index_all_pdfs():

    pdf_files = list(
        Path(DATA_DIR).glob("*.pdf")
    )

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in '{DATA_DIR}'"
        )

    all_chunks = []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    print("\nLoading PDFs...\n")

    for pdf_file in pdf_files:

        print(f"Processing: {pdf_file.name}")

        loader = PyPDFLoader(
            str(pdf_file)
        )

        documents = loader.load()

        chunks = splitter.split_documents(
            documents
        )

        for chunk in chunks:
            chunk.metadata["source"] = (
                pdf_file.name
            )

        all_chunks.extend(chunks)

        print(
            f"Indexed {len(chunks)} chunks "
            f"from {pdf_file.name}"
        )

    print(
        f"\nTotal chunks created: "
        f"{len(all_chunks)}"
    )

    embeddings = HuggingFaceEmbeddings(
        model_name=
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    if os.path.exists(CHROMA_DIR):

        print(
            "\nRemoving existing vector store..."
        )

        import shutil
        shutil.rmtree(CHROMA_DIR)

    Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )

    print(
        f"\nVector store created "
        f"successfully in '{CHROMA_DIR}'"
    )


if __name__ == "__main__":

    load_and_index_all_pdfs()
