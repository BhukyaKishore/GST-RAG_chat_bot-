import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DATA_DIR = "data"
    CHROMA_DB_DIR = "chroma_db"
    MODEL_NAME = "gpt-3.5-turbo"
    EMBEDDING_MODEL_NAME = "text-embedding-ada-002"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

config = Config()
