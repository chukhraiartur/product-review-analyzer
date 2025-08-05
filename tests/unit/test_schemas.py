"""Unit tests for Pydantic schemas."""


import pytest

from app.schemas.api import ProductResponse, ReviewResponse, SearchRequest
from app.schemas.vistaprint import VistaPrintProduct, VistaPrintReview


@pytest.mark.unit
class TestVistaPrintSchemas:
    """Test VistaPrint schemas."""

    def test_vistaprint_product_valid(self):
        """Test valid VistaPrint product data."""
        data = {
            "product_slug": "test-product",
            "name": "Test Product",
            "url": "https://www.vistaprint.com/test-product",
            "reviews": [],
        }

        product = VistaPrintProduct(**data)

        assert product.product_slug == "test-product"
        assert product.name == "Test Product"
        assert product.url == "https://www.vistaprint.com/test-product"
        assert product.reviews == []

    def test_vistaprint_review_valid(self):
        """Test valid VistaPrint review data."""
        data = {
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

        review = VistaPrintReview(**data)

        assert review.position == 1
        assert review.external_id == "123456"
        assert review.title == "Great Product"
        assert review.author == "Test User"
        assert review.score == 5
        assert review.description == "This is a great product!"
        assert review.is_verified_purchase is True
        assert review.images == []


@pytest.mark.unit
class TestAPISchemas:
    """Test API schemas."""

    def test_product_response_valid(self):
        """Test valid product response."""
        from datetime import datetime

        data = {
            "id": 1,
            "title": "Test Product",
            "url": "https://example.com/product",
            "source": "vistaprint",
            "reviews": [],
            "total_reviews": 0,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        response = ProductResponse(**data)

        assert response.id == 1
        assert response.title == "Test Product"
        assert response.url == "https://example.com/product"
        assert response.reviews == []

    def test_review_response_valid(self):
        """Test valid review response."""
        from datetime import datetime

        data = {
            "id": 1,
            "product_id": 1,
            "title": "Great Product",
            "text": "This is great!",
            "rating": 5,
            "author": "Test User",
            "date_posted": datetime.now(),
            "is_verified_purchase": True,
            "sentiment": "positive",
            "sentiment_score": 0.85,
            "image_urls": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        response = ReviewResponse(**data)

        assert response.id == 1
        assert response.product_id == 1
        assert response.title == "Great Product"
        assert response.text == "This is great!"
        assert response.rating == 5
        assert response.sentiment == "positive"
        assert response.sentiment_score == 0.85

    def test_search_request_valid(self):
        """Test valid search request."""
        data = {"query": "great quality", "limit": 10}

        request = SearchRequest(**data)

        assert request.query == "great quality"
        assert request.limit == 10

    def test_search_request_default_limit(self):
        """Test search request with default limit value."""
        data = {"query": "great quality"}

        request = SearchRequest(**data)

        assert request.query == "great quality"
        assert request.limit == 10  # Default value
