import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.db import get_vectorstore
from app.config import config

def load_documents():
    """Loads all PDF documents from the data directory."""
    documents = []
    if not os.path.exists(config.DATA_DIR):
        print(f"Data directory {config.DATA_DIR} not found.")
        return []

    for filename in os.listdir(config.DATA_DIR):
        if filename.endswith(".pdf"):
            file_path = os.path.join(config.DATA_DIR, filename)
            print(f"Loading {file_path}...")
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
    
    return documents

def split_documents(documents):
    """Splits documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def ingest_data():
    """Orchestrates the ingestion process."""
    print("Starting ingestion...")
    documents = load_documents()
    if not documents:
        print("No documents found to ingest.")
        return

    print(f"Loaded {len(documents)} document pages.")
    chunks = split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    print("Creating vector store...")
    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents=chunks)
    print("Ingestion complete. Vector store updated.")

if __name__ == "__main__":
    ingest_data()
