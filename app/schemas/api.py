"""API request and response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    """Base review model."""

    title: Optional[str] = Field(None, max_length=500, description="Review title")
    text: str = Field(
        ..., min_length=1, max_length=10000, description="Review text content"
    )
    rating: Optional[int] = Field(None, ge=1, le=5, description="Review rating (1-5)")
    author: Optional[str] = Field(
        None, max_length=255, description="Review author name"
    )
    date_posted: Optional[datetime] = Field(None, description="Review posting date")
    is_verified_purchase: bool = Field(
        False, description="Whether the purchase was verified"
    )
    position: Optional[int] = Field(None, ge=1, description="Review position")


class ReviewCreate(ReviewBase):
    """Model for creating a new review."""

    product_id: str = Field(..., description="Product identifier")
    external_id: Optional[str] = Field(None, description="External review ID")
    image_urls: Optional[list[str]] = Field(
        default_factory=list, description="Review image URLs"
    )


class ReviewResponse(ReviewBase):
    """Model for review response."""

    id: int = Field(..., description="Review ID")
    product_id: int = Field(..., description="Product identifier")
    external_id: Optional[str] = Field(None, description="External review ID")
    sentiment: str = Field(..., description="Sentiment analysis result")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score")
    image_urls: list[str] = Field(default_factory=list, description="Review image URLs")
    created_at: datetime = Field(..., description="Review creation timestamp")
    updated_at: datetime = Field(..., description="Review last update timestamp")

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    """Base product model."""

    title: str = Field(..., min_length=1, max_length=500, description="Product title")
    url: Optional[str] = Field(None, description="Product URL")
    source: str = Field("vistaprint", description="Data source")


class ProductCreate(ProductBase):
    """Model for creating a new product."""

    pass


class ProductResponse(ProductBase):
    """Model for product response."""

    id: int = Field(..., description="Product ID")
    reviews: list[ReviewResponse] = Field(
        default_factory=list, description="Product reviews"
    )
    total_reviews: int = Field(..., ge=0, description="Total number of reviews")
    average_rating: Optional[float] = Field(
        None, ge=0.0, le=5.0, description="Average rating"
    )
    sentiment_distribution: dict[str, int] = Field(
        default_factory=dict, description="Sentiment distribution"
    )
    created_at: datetime = Field(..., description="Product creation timestamp")
    updated_at: datetime = Field(..., description="Product last update timestamp")

    class Config:
        from_attributes = True


class ScrapingRequest(BaseModel):
    """Model for scraping request."""

    url: Optional[str] = Field(
        None, description="URL to scrape (optional for random mode)"
    )
    mode: str = Field("scrape", description="Scraping mode (scrape, mock, random)")
    force_refresh: Optional[bool] = Field(
        False, description="Force refresh HTML from website (ignore cached version)"
    )


class ScrapingResponse(BaseModel):
    """Model for scraping response."""

    product_id: int = Field(..., description="Product ID")
    product_title: str = Field(..., description="Product title")
    total_reviews: int = Field(..., ge=0, description="Total reviews scraped")
    total_images: int = Field(..., ge=0, description="Total images scraped")
    processing_time: float = Field(
        ..., ge=0.0, description="Processing time in seconds"
    )
    status: str = Field(..., description="Processing status")


class SearchRequest(BaseModel):
    """Model for search request."""

    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    product_id: Optional[str] = Field(None, description="Filter by product ID")
    sentiment: Optional[str] = Field(None, description="Filter by sentiment")
    limit: Optional[int] = Field(
        10, ge=1, le=100, description="Maximum results to return"
    )


class SearchResponse(BaseModel):
    """Model for search response."""

    query: str = Field(..., description="Search query")
    results: list[ReviewResponse] = Field(..., description="Search results")
    total_results: int = Field(..., ge=0, description="Total number of results")
    processing_time: float = Field(..., ge=0.0, description="Search processing time")


class HealthResponse(BaseModel):
    """Model for health check response."""

    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Application version")
    database_status: str = Field(..., description="Database connection status")
    vector_db_status: str = Field(..., description="Vector database status")
    storage_status: str = Field(..., description="Storage service status")
