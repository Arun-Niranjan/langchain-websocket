"""Configuration management using pydantic-settings."""

from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class CheckpointerType(StrEnum):
    """Supported checkpointer storage types."""

    MEMORY = "memory"
    POSTGRES = "postgres"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # OpenAI Configuration
    openai_api_key: str

    # Server Configuration
    server_host: str = "127.0.0.1"
    server_port: int = 3000

    # Checkpointer Configuration
    checkpointer_type: CheckpointerType = CheckpointerType.MEMORY

    # PostgreSQL Configuration
    postgres_user: str = "langchain"
    postgres_password: str = "langchain"
    postgres_db: str = "langchain"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    @property
    def postgres_connection_string(self) -> str:
        """Get PostgreSQL connection string."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


# Global settings instance
settings = Settings()
