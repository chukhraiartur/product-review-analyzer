"""Application configuration settings."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application settings
    app_name: str = Field(
        default="Product Review Analyzer", description="Application name"
    )
    debug: bool = Field(default=False, description="Debug mode")

    # Database settings - PostgreSQL (all required)
    db_host: str = Field(default="localhost", description="Database host")
    db_port: int = Field(default=5432, description="Database port")
    db_user: str = Field(default="review_user", description="Database user")
    db_password: str = Field(default="review_password", description="Database password")
    db_name: str = Field(default="review_analyzer", description="Database name")

    # Legacy database URL support (for backward compatibility)
    database_url: Optional[str] = Field(
        default=None, description="PostgreSQL database URL (legacy)"
    )

    # OpenAI settings
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(
        default="gpt-3.5-turbo", description="OpenAI model to use"
    )

    # Google Cloud Storage settings
    gcp_project_id: Optional[str] = Field(
        default=None, description="Google Cloud project ID"
    )
    gcp_bucket_name: Optional[str] = Field(
        default=None, description="Google Cloud Storage bucket name"
    )
    gcp_credentials_path: Optional[str] = Field(
        default=None, description="Path to GCP credentials file"
    )
    gcp_use_emulator: bool = Field(
        default=False, description="Use GCS emulator for local development"
    )
    gcp_emulator_host: Optional[str] = Field(
        default="localhost:4443", description="GCS emulator host"
    )

    # Vector database settings
    faiss_index_path: str = Field(
        default="./data/faiss_index", description="Path to FAISS index file"
    )

    # Scraping settings
    request_timeout: int = Field(
        default=30, description="HTTP request timeout in seconds"
    )
    max_retries: int = Field(
        default=3, description="Maximum number of retries for failed requests"
    )

    # API settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")

    @property
    def database_url_computed(self) -> str:
        """Construct database URL from individual components."""
        if self.database_url:
            return self.database_url

        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Global settings instance
settings = Settings()
