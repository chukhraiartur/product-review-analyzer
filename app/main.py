"""FastAPI application main module."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import health, products, search
from app.core.config import get_settings
from app.core.exceptions import ReviewAnalyzerException
from app.core.logging import setup_logging
from app.models.database import create_tables

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create FastAPI application with all setup."""
    settings = get_settings()
    
    # Setup logging
    setup_logging(
        log_level="DEBUG" if settings.debug else "INFO",
        log_file="logs/app.log" if settings.debug else None,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Starting Product Review Analyzer application")
        # Skip database operations in test environment
        if not settings.testing:
            try:
                create_tables()
                logger.info("Database tables created successfully")
            except Exception as e:
                logger.error(f"Failed to create database tables: {str(e)}")
                raise
        else:
            logger.info("Skipping database operations in test environment")
        yield
        logger.info("Shutting down Product Review Analyzer application")

    app = FastAPI(
        title=settings.app_name,
        description="Product Review Analyzer - AI-powered review analysis system",
        version="1.0.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(ReviewAnalyzerException)
    async def review_analyzer_exception_handler(request: Request, exc: ReviewAnalyzerException):
        logger.error(f"Application exception: {str(exc)}")
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(products.router, prefix="/api/v1", tags=["products"])
    app.include_router(search.router, prefix="/api/v1", tags=["search"])

    @app.get("/")
    async def root():
        return {
            "message": "Product Review Analyzer API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/api/v1/health",
        }

    @app.get("/docs")
    async def api_docs():
        return {"message": "API documentation available at /docs"}

    return app

# For normal run
app = create_app()
