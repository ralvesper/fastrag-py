from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./fastrag.db"  # fallback: SQLite local
    gemini_api_key: str = ""
    embedding_model: str = "gemini-embedding-001"
    embedding_dims: int = 1536
    chat_model: str = "gemini-2.5-flash-lite"

    # Lê variáveis do .env automaticamente
    model_config = {"env_file": ".env"}


# Instância única — importar de qualquer lugar: from config import settings
settings = Settings()
