"""FastAPI application main module."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import health, products, search
from app.core.config import settings
from app.core.exceptions import ReviewAnalyzerException
from app.core.logging import setup_logging
from app.models.database import create_tables

# Setup logging
setup_logging(
    log_level="DEBUG" if settings.debug else "INFO",
    log_file="logs/app.log" if settings.debug else None,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Product Review Analyzer application")

    try:
        # Create database tables
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Product Review Analyzer application")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Product Review Analyzer - AI-powered review analysis system",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ReviewAnalyzerException)
async def review_analyzer_exception_handler(
    request: Request, exc: ReviewAnalyzerException
):
    """Handle custom application exceptions."""
    logger.error(f"Application exception: {str(exc)}")
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Include API routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Product Review Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


@app.get("/docs")
async def api_docs():
    """API documentation endpoint."""
    return {"message": "API documentation available at /docs"}
