"""Pytest configuration and fixtures for testing."""

import os
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import create_app
from app.models.database.base import Base
from app.services.gcs_service import GCSService
from app.services.llm import LLMService
from app.services.vector_db import VectorDBService


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine."""
    # Use in-memory SQLite for tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def test_db_session(test_db_engine):
    """Create test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def mock_gcs_service():
    """Mock GCS service."""
    mock_service = Mock(spec=GCSService)
    mock_service.client = Mock()
    mock_service.bucket = Mock()
    mock_service.bucket.name = "test-bucket"

    # Mock methods
    mock_service.save_html.return_value = (
        "https://storage.googleapis.com/test-bucket/test.html"
    )
    mock_service.save_image.return_value = (
        "https://storage.googleapis.com/test-bucket/test.jpg"
    )
    mock_service.save_logs.return_value = (
        "https://storage.googleapis.com/test-bucket/test.log"
    )
    mock_service.download_image.return_value = b"fake_image_data"
    mock_service.list_product_images.return_value = []
    mock_service.delete_old_files.return_value = 0
    mock_service._get_recent_html.return_value = None

    return mock_service


@pytest.fixture
def mock_llm_service():
    """Mock LLM service."""
    mock_service = Mock(spec=LLMService)
    mock_service.analyze_sentiment.return_value = {
        "sentiment": "positive",
        "score": 0.85,
        "confidence": 0.9,
    }
    return mock_service


@pytest.fixture
def mock_vector_db_service():
    """Mock Vector DB service."""
    mock_service = Mock(spec=VectorDBService)
    mock_service.add_reviews.return_value = True
    mock_service.search_reviews.return_value = []
    mock_service.get_review_by_id.return_value = None
    return mock_service


@pytest.fixture
def mock_settings():
    """Mock application settings."""
    with patch("app.core.config.settings") as mock:
        mock.openai_api_key = "test-key"
        mock.openai_model = "gpt-3.5-turbo"
        mock.gcp_project_id = "test-project"
        mock.gcp_bucket_name = "test-bucket"
        mock.gcp_credentials_path = "./credentials/test-credentials.json"
        mock.database_url = "sqlite:///:memory:"
        mock.faiss_index_path = "./data/test_faiss_index"
        yield mock


@pytest.fixture
def test_client(mock_gcs_service, mock_llm_service, mock_vector_db_service, test_db_session):
    """Create test client with mocked dependencies."""
    app = create_app()
    with patch("app.api.dependencies.get_gcs_service", return_value=mock_gcs_service), patch(
        "app.api.dependencies.get_llm_service", return_value=mock_llm_service
    ), patch("app.api.dependencies.get_vector_db_service", return_value=mock_vector_db_service), patch(
        "app.api.dependencies.get_db", return_value=test_db_session
    ):
        with TestClient(app) as client:
            yield client


@pytest.fixture
def mock_requests():
    """Mock requests library."""
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # Default successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test HTML</body></html>"
        mock_response.content = b"<html><body>Test HTML</body></html>"
        mock_response.json.return_value = {"test": "data"}

        mock_get.return_value = mock_response
        mock_post.return_value = mock_response

        yield {"get": mock_get, "post": mock_post}


@pytest.fixture
def mock_openai():
    """Mock OpenAI API."""
    with patch("openai.ChatCompletion.create") as mock_create:
        mock_create.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"sentiment": "positive", "score": 0.85, "confidence": 0.9}'
                    }
                }
            ]
        }
        yield mock_create


@pytest.fixture
def mock_faiss():
    """Mock FAISS vector database."""
    with patch("faiss.IndexFlatL2") as mock_index:
        mock_index_instance = Mock()
        mock_index_instance.add.return_value = None
        mock_index_instance.search.return_value = ([], [])
        mock_index.return_value = mock_index_instance
        yield mock_index


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    # Set test environment
    os.environ["TESTING"] = "true"
    os.environ["DEBUG"] = "true"
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["OPENAI_MODEL"] = "gpt-3.5-turbo"
    os.environ["GCP_PROJECT_ID"] = "test-project"
    os.environ["GCP_BUCKET_NAME"] = "test-bucket"
    os.environ["GCP_CREDENTIALS_PATH"] = "./credentials/test-credentials.json"
    os.environ["FAISS_INDEX_PATH"] = "./test_data/faiss_index"
    os.environ["REQUEST_TIMEOUT"] = "10"
    os.environ["MAX_RETRIES"] = "1"
    os.environ["API_HOST"] = "0.0.0.0"
    os.environ["API_PORT"] = "8000"
    
    # Database settings for tests (use SQLite)
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_PORT"] = "5432"
    os.environ["DB_USER"] = "test_user"
    os.environ["DB_PASSWORD"] = "test_password"
    os.environ["DB_NAME"] = "test_db"

    yield

    # Cleanup
    for key in [
        "TESTING", "DEBUG", "OPENAI_API_KEY", "OPENAI_MODEL", "GCP_PROJECT_ID",
        "GCP_BUCKET_NAME", "GCP_CREDENTIALS_PATH", "FAISS_INDEX_PATH",
        "REQUEST_TIMEOUT", "MAX_RETRIES", "API_HOST", "API_PORT",
        "DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"
    ]:
        os.environ.pop(key, None)


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "product_slug": "test-product",
        "name": "Test Product",
        "url": "https://www.vistaprint.com/test-product",
        "reviews": [
            {
                "position": 1,
                "external_id": "123456",
                "title": "Great Product",
                "date_posted": "2025-01-01 00:00:00",
                "author": "Test User",
                "score": 5,
                "description": "This is a great product!",
                "is_verified_purchase": True,
                "images": [],
            }
        ],
    }


@pytest.fixture
def sample_review_data():
    """Sample review data for testing."""
    return {
        "position": 1,
        "external_id": "123456",
        "title": "Great Product",
        "date_posted": "2025-01-01 00:00:00",
        "author": "Test User",
        "score": 5,
        "description": "This is a great product!",
        "is_verified_purchase": True,
        "images": [],
    }
