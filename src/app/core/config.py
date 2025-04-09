"""Configuration settings for the application."""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Project metadata
    PROJECT_NAME: str = "Vector DB Gateway"
    PROJECT_DESCRIPTION: str = "API-key secured FastAPI microservice for Qdrant vector database"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    DOCS_URL: str = "/docs"
    LOG_LEVEL: str = "INFO"  # Default log level

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["*"]

    # Database settings
    DATABASE_URL: str
    DB_ECHO: bool = False

    # Qdrant settings
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""

    # Security settings
    API_KEY_HEADER_NAME: str = "X-API-Key"
    
    # Model settings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_API_KEY: str = ""
    SIMILARITY_THRESHOLD: float = 0.75  # Threshold for vector similarity matching

    # Add JWT authentication settings
    JWT_SECRET: str
    JWT_ALGORITHM: str

    COLLECTION_NAME_SUFFIX: str = "_knowledge_base"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()