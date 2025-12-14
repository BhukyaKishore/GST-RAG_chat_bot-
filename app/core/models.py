from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from app.config import config

def get_llm():
    """Returns the configured ChatOpenAI instance."""
    return ChatOpenAI(
        model=config.MODEL_NAME,
        temperature=0,
        openai_api_key=config.OPENAI_API_KEY
    )

def get_embedding_model():
    """Returns the configured OpenAIEmbeddings instance."""
    return OpenAIEmbeddings(
        model=config.EMBEDDING_MODEL_NAME,
        openai_api_key=config.OPENAI_API_KEY
    )
