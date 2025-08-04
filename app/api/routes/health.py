"""Health check endpoints."""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import get_database, get_gcs_service, get_vector_db_service
from app.core.config import settings
from app.schemas import HealthResponse
from app.services.gcs_service import GCSService
from app.services.vector_db import VectorDBService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health_check(
    db: Session = Depends(get_database),
    gcs_service: GCSService = Depends(get_gcs_service),
    vector_db_service: VectorDBService = Depends(get_vector_db_service),
) -> HealthResponse:
    """
    Check application health and dependencies status.

    Returns:
        Health status of the application and all dependencies
    """
    try:
        # Check database connection
        db_status = "healthy"
        try:
            db.execute(text("SELECT 1"))
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            db_status = "unhealthy"

        # Check vector database
        vector_db_status = "healthy"
        try:
            vector_db_service.get_stats()
        except Exception as e:
            logger.error(f"Vector database health check failed: {str(e)}")
            vector_db_status = "unhealthy"

        # Check storage service
        storage_status = "healthy"
        try:
            # Simple check - try to list a few blobs
            list(gcs_service.client.list_blobs(gcs_service.bucket, max_results=1))
        except Exception as e:
            logger.error(f"Storage service health check failed: {str(e)}")
            storage_status = "unhealthy"

        # Determine overall status
        overall_status = "healthy"
        if any(
            status == "unhealthy"
            for status in [db_status, vector_db_status, storage_status]
        ):
            overall_status = "degraded"

        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now(),
            version=settings.app_name,
            database_status=db_status,
            vector_db_status=vector_db_status,
            storage_status=storage_status,
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/ready")
async def readiness_check(
    db: Session = Depends(get_database),
) -> dict[str, str]:
    """
    Check if the application is ready to serve requests.

    Returns:
        Readiness status
    """
    try:
        # Check database connection
        db.execute(text("SELECT 1"))

        return {"status": "ready"}

    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/live")
async def liveness_check() -> dict[str, str]:
    """
    Check if the application is alive.

    Returns:
        Liveness status
    """
    return {"status": "alive"}
