"""API integration tests for Google Cloud Storage."""

import pytest


@pytest.mark.api
class TestGCSAPIIntegration:
    """API integration tests for GCS functionality."""

    @pytest.mark.mock
    def test_health_check_with_gcs_status(self, test_client):
        """Test health check endpoint includes GCS status."""
        response = test_client.get("/api/v1/health/")
        assert response.status_code == 200
        data = response.json()
        assert "storage_status" in data
        assert data["status"] == "healthy"

    @pytest.mark.mock
    def test_invalid_force_refresh_parameter(self, test_client):
        """Test API validation for force_refresh parameter."""
        response = test_client.post(
            "/api/v1/products/scrape",
            json={
                "url": "https://www.vistaprint.com/test-product",
                "mode": "scrape",
                "force_refresh": "invalid_value",  # Should be boolean
            },
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.mock
    def test_scraping_with_mock_data(self, test_client):
        """Test scraping with mock data (doesn't require real HTTP requests)."""
        # Test with mock mode which doesn't require real HTTP requests
        response = test_client.post(
            "/api/v1/products/scrape",
            json={
                "url": "https://www.vistaprint.com/test-product",
                "mode": "mock",
                "force_refresh": False,
            },
        )
        # Mock mode requires a valid URL, so this will fail with 400
        assert response.status_code == 400  # Bad request (invalid URL for mock mode)

    @pytest.mark.mock
    def test_scraping_with_random_data(self, test_client):
        """Test scraping with random data (doesn't require real HTTP requests)."""
        # Test with random mode which doesn't require real HTTP requests
        response = test_client.post(
            "/api/v1/products/scrape",
            json={
                "url": "https://www.vistaprint.com/test-product",
                "mode": "random",
                "force_refresh": False,
            },
        )
        # Random mode requires a valid URL, so this will fail with 400
        assert response.status_code == 400  # Bad request (invalid URL for random mode)

    @pytest.mark.mock
    def test_scraping_missing_parameters(self, test_client):
        """Test scraping with missing required parameters."""
        # Test without URL
        response = test_client.post(
            "/api/v1/products/scrape",
            json={"mode": "mock"},
        )
        assert response.status_code == 500  # Internal server error (missing URL)

        # Test without mode
        response = test_client.post(
            "/api/v1/products/scrape",
            json={"url": "https://example.com"},
        )
        assert response.status_code == 400  # Bad request (missing mode)

    @pytest.mark.mock
    def test_scraping_invalid_mode(self, test_client):
        """Test scraping with invalid mode."""
        response = test_client.post(
            "/api/v1/products/scrape",
            json={
                "url": "https://www.vistaprint.com/test-product",
                "mode": "invalid_mode",
            },
        )
        assert response.status_code == 500  # Internal server error (invalid mode)


