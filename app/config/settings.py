"""
Application settings with environment variable support
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Qdrant Configuration
    qdrant_url: str = Field(
        default="http://localhost:6333",
        description="Qdrant instance URL"
    )
    qdrant_api_key: Optional[str] = Field(
        default=None,
        description="Qdrant API key"
    )

    # OpenAI Configuration
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key for embeddings"
    )
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model"
    )

    # Mem0 Configuration
    mem0_collection: str = Field(
        default="user_memories",
        description="Qdrant collection name"
    )
    mem0_host: str = Field(
        default="0.0.0.0",
        description="Server host"
    )
    mem0_port: int = Field(
        default=8002,
        description="Server port"
    )

    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["*"],
        description="CORS allowed origins"
    )

    # Logging Configuration
    log_level: str = Field(
        default="info",
        description="Log level"
    )
    debug: bool = Field(
        default=False,
        description="Debug mode"
    )

    # Application Info
    app_name: str = Field(
        default="Mem0 Server",
        description="Application name"
    )
    app_version: str = Field(
        default="1.0.0",
        description="Application version"
    )


# Global settings instance
settings = Settings()
