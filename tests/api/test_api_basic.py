"""Basic API tests with mocks."""


import pytest


@pytest.mark.api
class TestBasicAPI:
    """Test basic API endpoints."""

    @pytest.mark.unit
    def test_root_endpoint(self, test_client):
        """Test root endpoint."""
        response = test_client.get("/")
        assert response.status_code == 200
        assert "Product Review Analyzer" in response.json()["message"]

    @pytest.mark.unit
    def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/api/v1/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database_status" in data
        assert "storage_status" in data

    @pytest.mark.unit
    def test_api_docs_available(self, test_client):
        """Test that API docs are available."""
        response = test_client.get("/docs")
        assert response.status_code == 200

    @pytest.mark.unit
    def test_redoc_available(self, test_client):
        """Test that ReDoc is available."""
        response = test_client.get("/redoc")
        assert response.status_code == 200

    @pytest.mark.mock
    def test_products_list_empty(self, test_client):
        """Test products list when empty."""
        # This test works with mocks and doesn't require real database
        response = test_client.get("/api/v1/products/")
        assert response.status_code == 200
        # In test environment, we might have products or empty list
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.mock
    def test_product_not_found(self, test_client):
        """Test product not found."""
        # Test with a very high ID that shouldn't exist
        response = test_client.get("/api/v1/products/999999")
        assert response.status_code == 404

    @pytest.mark.unit
    def test_search_stats(self, test_client):
        """Test search statistics endpoint."""
        response = test_client.get("/api/v1/search/stats")
        assert response.status_code == 200
        data = response.json()
        assert "vector_database" in data
        assert "search_available" in data

    @pytest.mark.mock
    def test_search_reviews_empty(self, test_client):
        """Test search reviews when no results."""
        # Test with a query that should return empty results
        response = test_client.post(
            "/api/v1/search/reviews", json={"query": "nonexistent_query_xyz123", "k": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "results" in data

    @pytest.mark.unit
    def test_scraping_invalid_url(self, test_client):
        """Test scraping with invalid URL."""
        response = test_client.post(
            "/api/v1/products/scrape",
            json={"url": "invalid-url", "mode": "scrape", "force_refresh": False},
        )
        assert response.status_code == 400  # Bad request (invalid URL)

    @pytest.mark.unit
    def test_scraping_missing_url(self, test_client):
        """Test scraping with missing URL."""
        response = test_client.post(
            "/api/v1/products/scrape",
            json={"mode": "scrape"},
        )
        assert response.status_code == 400  # Bad request (missing URL)

    @pytest.mark.unit
    def test_scraping_invalid_mode(self, test_client):
        """Test scraping with invalid mode."""
        response = test_client.post(
            "/api/v1/products/scrape",
            json={"url": "https://example.com", "mode": "invalid_mode"},
        )
        assert response.status_code == 500  # Internal server error (invalid mode)
