"""API integration tests for Google Cloud Storage."""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestGCSAPIIntegration:
    """API integration tests for GCS functionality."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_gcs_service(self):
        """Mock GCS service."""
        with patch("app.services.gcs_service.GCSService") as mock_service:
            mock_instance = Mock()
            mock_instance.save_html.return_value = (
                "https://storage.googleapis.com/test-bucket/html/test.html"
            )
            mock_instance.download_image.return_value = b"fake_image_data"
            mock_instance.save_image.return_value = (
                "https://storage.googleapis.com/test-bucket/images/test.jpg"
            )
            mock_service.return_value = mock_instance
            yield mock_instance

    @pytest.mark.api
    @patch("app.services.vistaprint_scraper.requests.get")
    def test_scraping_with_force_refresh_true(self, mock_get, client, mock_gcs_service):
        """Test scraping API with force_refresh=True."""

        # Mock HTTP responses for both product page and reviews API
        def mock_get_side_effect(url, **kwargs):
            mock_response = Mock()
            if "rating-reviews.prod.merch.vpsvc.com" in url:
                # Mock reviews API response
                mock_response.text = '{"reviews": [], "total": 0}'
            else:
                # Mock product page response
                mock_response.text = """
                <html>
                    <head>
                        <meta name="pageName" content="test-product-api-integration:Product">
                        <title>Test Product</title>
                    </head>
                    <body>
                        <div class="swan-site-main">
                            <div class="swan-grid-container">
                                <h1>Test Product Name</h1>
                            </div>
                        </div>
                    </body>
                </html>
                """
            mock_response.raise_for_status.return_value = None
            return mock_response

        mock_get.side_effect = mock_get_side_effect

        # Test API call
        response = client.post(
            "/api/v1/products/scrape",
            json={
                "url": "https://www.vistaprint.com/test-product",
                "mode": "scrape",
                "force_refresh": True,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

        # Verify GCS service was called
        mock_gcs_service.save_html.assert_called()

    @pytest.mark.api
    def test_scraping_with_force_refresh_false(self, client, mock_gcs_service):
        """Test scraping API with force_refresh=False (default)."""
        # Mock GCS service methods
        mock_gcs_service.save_html.return_value = (
            "https://storage.googleapis.com/test-bucket/html/test.html"
        )
        mock_gcs_service.download_image.return_value = b"fake_image_data"
        mock_gcs_service.save_image.return_value = (
            "https://storage.googleapis.com/test-bucket/images/test.jpg"
        )

        # Mock other services
        with patch("app.services.vistaprint_scraper.VistaPrintScraper") as mock_scraper:
            mock_scraper_instance = Mock()
            mock_scraper.return_value = mock_scraper_instance

            # Mock scraped data
            mock_product = Mock()
            mock_product.product_slug = "test-product"
            mock_product.name = "Test Product"
            mock_product.url = "https://example.com/test"
            mock_product.reviews = []

            mock_scraper_instance.get_product_info.return_value = mock_product

            # Test API call without force_refresh (should default to False)
            response = client.post(
                "/api/v1/products/scrape",
                json={
                    "url": "https://www.vistaprint.com/test-product",
                    "mode": "scrape",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"

            # Verify force_refresh defaults to False
            mock_scraper.assert_called_once_with(
                url="https://www.vistaprint.com/test-product",
                mode="scrape",
                force_refresh=False,
            )

    @pytest.mark.api
    def test_scraping_with_gcs_html_caching(self, client, mock_gcs_service):
        """Test that GCS HTML caching is used when force_refresh=False."""
        # Mock GCS service to return existing HTML (simulating cache hit)
        mock_gcs_service._get_recent_html.return_value = (
            "https://storage.googleapis.com/test-bucket/html/cached.html"
        )
        mock_gcs_service.save_html.return_value = (
            "https://storage.googleapis.com/test-bucket/html/cached.html"
        )

        # Mock other services
        with patch("app.services.vistaprint_scraper.VistaPrintScraper") as mock_scraper:
            mock_scraper_instance = Mock()
            mock_scraper.return_value = mock_scraper_instance

            # Mock scraped data
            mock_product = Mock()
            mock_product.product_slug = "test-product"
            mock_product.name = "Test Product"
            mock_product.url = "https://example.com/test"
            mock_product.reviews = []

            mock_scraper_instance.get_product_info.return_value = mock_product

            # Test API call
            response = client.post(
                "/api/v1/products/scrape",
                json={
                    "url": "https://www.vistaprint.com/test-product",
                    "mode": "scrape",
                    "force_refresh": False,
                },
            )

            assert response.status_code == 200

            # Verify that GCS caching was checked
            mock_gcs_service._get_recent_html.assert_called()

    @pytest.mark.api
    def test_scraping_with_image_storage(self, client, mock_gcs_service):
        """Test that images are stored in GCS during scraping."""
        # Mock GCS service methods
        mock_gcs_service.save_html.return_value = (
            "https://storage.googleapis.com/test-bucket/html/test.html"
        )
        mock_gcs_service.download_image.return_value = b"fake_image_data"
        mock_gcs_service.save_image.return_value = (
            "https://storage.googleapis.com/test-bucket/images/test.jpg"
        )

        # Mock other services
        with patch("app.services.vistaprint_scraper.VistaPrintScraper") as mock_scraper:
            mock_scraper_instance = Mock()
            mock_scraper.return_value = mock_scraper_instance

            # Mock scraped data with images
            mock_review = Mock()
            mock_review.external_id = "123"
            mock_review.images = [
                "http://example.com/image1.jpg",
                "http://example.com/image2.jpg",
            ]

            mock_product = Mock()
            mock_product.product_slug = "test-product"
            mock_product.name = "Test Product"
            mock_product.url = "https://example.com/test"
            mock_product.reviews = [mock_review]

            mock_scraper_instance.get_product_info.return_value = mock_product

            # Test API call
            response = client.post(
                "/api/v1/products/scrape",
                json={
                    "url": "https://www.vistaprint.com/test-product",
                    "mode": "scrape",
                },
            )

            assert response.status_code == 200

            # Verify that images were downloaded and stored
            assert mock_gcs_service.download_image.call_count == 2
            assert mock_gcs_service.save_image.call_count == 2

    @pytest.mark.api
    def test_scraping_with_gcs_failure_handling(self, client, mock_gcs_service):
        """Test that scraping continues even if GCS operations fail."""
        # Mock GCS service to fail
        mock_gcs_service.save_html.return_value = None
        mock_gcs_service.download_image.return_value = None
        mock_gcs_service.save_image.return_value = None

        # Mock other services
        with patch("app.services.vistaprint_scraper.VistaPrintScraper") as mock_scraper:
            mock_scraper_instance = Mock()
            mock_scraper.return_value = mock_scraper_instance

            # Mock scraped data
            mock_product = Mock()
            mock_product.product_slug = "test-product"
            mock_product.name = "Test Product"
            mock_product.url = "https://example.com/test"
            mock_product.reviews = []

            mock_scraper_instance.get_product_info.return_value = mock_product

            # Test API call - should still succeed even if GCS fails
            response = client.post(
                "/api/v1/products/scrape",
                json={
                    "url": "https://www.vistaprint.com/test-product",
                    "mode": "scrape",
                },
            )

            # Should still return 200 even if GCS operations failed
            assert response.status_code == 200

    @pytest.mark.api
    def test_health_check_with_gcs_status(self, client):
        """Test health check endpoint includes GCS status."""
        with patch("app.services.gcs_service.GCSService") as mock_gcs_service:
            mock_gcs_service.return_value = Mock()

            response = client.get("/api/v1/health/")

            assert response.status_code == 200
            data = response.json()
            assert "storage_status" in data
            # Note: In a real implementation, this would check actual GCS connectivity

    @pytest.mark.api
    def test_invalid_force_refresh_parameter(self, client):
        """Test API validation for force_refresh parameter."""
        response = client.post(
            "/api/v1/products/scrape",
            json={
                "url": "https://www.vistaprint.com/test-product",
                "mode": "scrape",
                "force_refresh": "invalid_value",  # Should be boolean
            },
        )

        # Should return 422 for validation error
        assert response.status_code == 422

    @pytest.mark.api
    def test_missing_force_refresh_parameter(self, client, mock_gcs_service):
        """Test that force_refresh defaults to False when not provided."""
        # Mock GCS service methods
        mock_gcs_service.save_html.return_value = (
            "https://storage.googleapis.com/test-bucket/html/test.html"
        )

        # Mock other services
        with patch("app.services.vistaprint_scraper.VistaPrintScraper") as mock_scraper:
            mock_scraper_instance = Mock()
            mock_scraper.return_value = mock_scraper_instance

            # Mock scraped data
            mock_product = Mock()
            mock_product.product_slug = "test-product"
            mock_product.name = "Test Product"
            mock_product.url = "https://example.com/test"
            mock_product.reviews = []

            mock_scraper_instance.get_product_info.return_value = mock_product

            # Test API call without force_refresh parameter
            response = client.post(
                "/api/v1/products/scrape",
                json={
                    "url": "https://www.vistaprint.com/test-product",
                    "mode": "scrape",
                },
            )

            assert response.status_code == 200

            # Verify force_refresh defaults to False
            mock_scraper.assert_called_once_with(
                url="https://www.vistaprint.com/test-product",
                mode="scrape",
                force_refresh=False,
            )
