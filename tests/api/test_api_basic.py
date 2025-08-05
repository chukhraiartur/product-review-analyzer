"""Basic API tests with mocks."""

from unittest.mock import Mock, patch

import pytest


@pytest.mark.api
class TestBasicAPI:
    """Test basic API endpoints."""

    def test_root_endpoint(self, test_client):
        """Test root endpoint."""
        response = test_client.get("/")
        assert response.status_code == 200
        assert "Product Review Analyzer" in response.json()["message"]

    def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/api/v1/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database_status" in data
        assert "storage_status" in data

    def test_api_docs_available(self, test_client):
        """Test that API docs are available."""
        response = test_client.get("/docs")
        assert response.status_code == 200

    def test_redoc_available(self, test_client):
        """Test that ReDoc is available."""
        response = test_client.get("/redoc")
        assert response.status_code == 200

    def test_products_list_empty(self, test_client):
        """Test products list when empty."""
        with patch("app.api.routes.products.get_db") as mock_db:
            mock_session = Mock()
            mock_session.query.return_value.all.return_value = []
            mock_db.return_value = mock_session

            response = test_client.get("/api/v1/products/")
            assert response.status_code == 200
            assert response.json() == []

    def test_product_not_found(self, test_client):
        """Test product not found."""
        with patch("app.api.routes.products.get_db") as mock_db:
            mock_session = Mock()
            mock_session.query.return_value.filter.return_value.first.return_value = (
                None
            )
            mock_db.return_value = mock_session

            response = test_client.get("/api/v1/products/999")
            assert response.status_code == 404

    def test_search_stats(self, test_client):
        """Test search statistics endpoint."""
        with patch("app.api.routes.search.get_db") as mock_db:
            mock_session = Mock()
            mock_session.query.return_value.count.return_value = 0
            mock_db.return_value = mock_session

            response = test_client.get("/api/v1/search/stats")
            assert response.status_code == 200
            data = response.json()
            assert "total_reviews" in data
            assert "sentiment_distribution" in data

    def test_search_reviews_empty(self, test_client):
        """Test search reviews when no results."""
        with patch("app.api.dependencies.get_vector_db_service") as mock_vector:
            mock_service = Mock()
            mock_service.search_reviews.return_value = []
            mock_vector.return_value = mock_service

            response = test_client.post(
                "/api/v1/search/reviews", json={"query": "test query", "k": 5}
            )
            assert response.status_code == 200
            assert response.json() == []

    def test_scraping_invalid_url(self, test_client):
        """Test scraping with invalid URL."""
        response = test_client.post(
            "/api/v1/products/scrape",
            json={"url": "invalid-url", "mode": "scrape", "force_refresh": False},
        )
        assert response.status_code == 422  # Validation error
