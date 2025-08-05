"""FastAPI dependencies."""


from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.database import get_db
from app.services.data_service import DataService
from app.services.gcs_service import GCSService
from app.services.llm import LLMService
from app.services.vector_db import VectorDBService
from app.services.vistaprint_scraper import VistaPrintScraper

logger = get_logger(__name__)


def get_llm_service() -> LLMService:
    """Get LLM service instance."""
    return LLMService()


def get_vistaprint_scraper_service() -> VistaPrintScraper:
    """Get VistaPrint scraper service instance."""
    # Create GCS service directly to avoid circular dependency
    gcs_service = GCSService()
    return VistaPrintScraper(gcs_service=gcs_service)


def get_gcs_service() -> GCSService:
    """Get Google Cloud Storage service instance."""
    return GCSService()


def get_vector_db_service() -> VectorDBService:
    """Get vector database service instance."""
    return VectorDBService()


def get_data_service(
    db: Session = Depends(get_db),
    llm_service: LLMService = Depends(get_llm_service),
    gcs_service: GCSService = Depends(get_gcs_service),
    vector_db_service: VectorDBService = Depends(get_vector_db_service),
) -> DataService:
    """Get data service instance."""
    return DataService(db, llm_service, gcs_service, vector_db_service)


def get_database() -> Session:
    """Get database session."""
    db_generator = get_db()
    if hasattr(db_generator, '__next__'):
        # It's a generator, get the first value
        return next(db_generator)
    else:
        # It's already a Session object (e.g., in tests)
        return db_generator
