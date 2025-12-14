from langchain_chroma import Chroma
from app.core.models import get_embedding_model
from app.config import config
import os

def get_vectorstore():
    """Returns the Chroma vectorstore instance."""
    embedding_function = get_embedding_model()
    
    # Check if directory exists, if not it will be created by Chroma
    return Chroma(
        persist_directory=config.CHROMA_DB_DIR,
        embedding_function=embedding_function
    )
