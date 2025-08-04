"""Pydantic schemas package."""

from .api import (
    HealthResponse,
    ProductBase,
    ProductCreate,
    ProductResponse,
    ReviewBase,
    ReviewCreate,
    ReviewResponse,
    ScrapingRequest,
    ScrapingResponse,
    SearchRequest,
    SearchResponse,
)
from .vistaprint import VistaPrintProduct, VistaPrintReview

__all__ = [
    # API schemas
    "ProductBase",
    "ProductCreate",
    "ProductResponse",
    "ReviewBase",
    "ReviewCreate",
    "ReviewResponse",
    "ScrapingRequest",
    "ScrapingResponse",
    "SearchRequest",
    "SearchResponse",
    "HealthResponse",
    # VistaPrint schemas
    "VistaPrintProduct",
    "VistaPrintReview",
]
