"""VistaPrint-specific data schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class VistaPrintReview(BaseModel):
    """VistaPrint review data structure."""

    position: int = Field(..., description="Review position")
    external_id: str = Field(..., description="External review ID")
    title: Optional[str] = Field(None, description="Review title")
    date_posted: Optional[str] = Field(None, description="Review posting date")
    author: Optional[str] = Field(None, description="Review author")
    score: Optional[int] = Field(None, description="Review score")
    description: str = Field(..., description="Review text content")
    is_verified_purchase: bool = Field(False, description="Verified purchase status")
    images: list[str] = Field(default_factory=list, description="Review images")


class VistaPrintProduct(BaseModel):
    """VistaPrint product data structure."""

    product_slug: str = Field(..., description="Product slug from VistaPrint")
    name: str = Field(..., description="Product name")
    url: str = Field(..., description="Product URL")
    reviews: list[VistaPrintReview] = Field(
        default_factory=list, description="Product reviews"
    )
