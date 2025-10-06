"""Configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


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


# Global settings instance
settings = Settings()
