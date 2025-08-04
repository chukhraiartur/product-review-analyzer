"""Integration tests for GCS and VistaPrint scraper integration."""

from unittest.mock import Mock, patch

import pytest

from app.services.gcs_service import GCSService
from app.services.vistaprint_scraper import ScrapingMode, VistaPrintScraper


class TestGCSVistaPrintIntegration:
    """Integration tests for GCS and VistaPrint scraper."""

    @pytest.fixture
    def mock_gcs_service(self):
        """Create mock GCS service."""
        mock_service = Mock(spec=GCSService)
        mock_service.save_html.return_value = (
            "https://storage.googleapis.com/test-bucket/html/test.html"
        )
        return mock_service

    @pytest.fixture
    def mock_html_content(self):
        """Create mock HTML content."""
        return """
        <html>
            <head>
                <meta name="pageName" content="paperCoasters:Product">
                <title>Test Product</title>
            </head>
            <body>
                <div class="swan-site-main">
                    <div class="swan-grid-container">
                        <h1>Test Product Name</h1>
                    </div>
                </div>
                <div id="reviews-container">
                    <div class="review-item">
                        <h3>Great Product</h3>
                        <p>This is a great product!</p>
                    </div>
                </div>
            </body>
        </html>
        """

    @pytest.mark.integration
    def test_scraper_initialization_with_gcs(self, mock_gcs_service):
        """Test scraper initialization with GCS service."""
        scraper = VistaPrintScraper(
            url="https://example.com/test",
            mode=ScrapingMode.SCRAPE,
            force_refresh=True,
            gcs_service=mock_gcs_service,
        )

        assert scraper.gcs_service is not None
        assert scraper.force_refresh is True
        assert scraper.url == "https://example.com/test"

    @pytest.mark.integration
    def test_scraper_initialization_without_gcs(self):
        """Test scraper initialization without GCS service."""
        scraper = VistaPrintScraper(
            url="https://example.com/test",
            mode=ScrapingMode.SCRAPE,
            force_refresh=False,
        )

        assert scraper.gcs_service is None
        assert scraper.force_refresh is False

    @pytest.mark.integration
    @patch("app.services.vistaprint_scraper.requests.get")
    def test_parse_product_with_gcs_html_saving(
        self, mock_get, mock_gcs_service, mock_html_content
    ):
        """Test that HTML is saved to GCS during product parsing."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.text = mock_html_content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        scraper = VistaPrintScraper(
            url="https://example.com/test",
            mode=ScrapingMode.SCRAPE,
            force_refresh=True,
            gcs_service=mock_gcs_service,
        )

        # Parse product
        result = scraper.parse_product("https://example.com/test")

        # Verify GCS service was called
        mock_gcs_service.save_html.assert_called_once()
        call_args = mock_gcs_service.save_html.call_args
        assert call_args[1]["product_slug"] == "paperCoasters"
        assert call_args[1]["html_content"] == mock_html_content
        assert call_args[1]["force_refresh"] is True

        # Verify result
        assert result["product_slug"] == "paperCoasters"
        assert result["name"] == "Test Product Name"
        assert result["url"] == "https://example.com/test"

    @pytest.mark.integration
    @patch("app.services.vistaprint_scraper.requests.get")
    def test_parse_product_without_gcs(self, mock_get, mock_html_content):
        """Test product parsing without GCS service."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.text = mock_html_content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        scraper = VistaPrintScraper(
            url="https://example.com/test",
            mode=ScrapingMode.SCRAPE,
            force_refresh=False,
        )

        # Parse product
        result = scraper.parse_product("https://example.com/test")

        # Verify result (should work without GCS)
        assert result["product_slug"] == "paperCoasters"
        assert result["name"] == "Test Product Name"
        assert result["url"] == "https://example.com/test"

    @pytest.mark.integration
    @patch("app.services.vistaprint_scraper.requests.get")
    def test_parse_product_gcs_failure_handling(
        self, mock_get, mock_gcs_service, mock_html_content
    ):
        """Test that scraping continues even if GCS saving fails."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.text = mock_html_content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Mock GCS service to fail
        mock_gcs_service.save_html.side_effect = Exception("GCS error")

        scraper = VistaPrintScraper(
            url="https://example.com/test",
            mode=ScrapingMode.SCRAPE,
            force_refresh=True,
            gcs_service=mock_gcs_service,
        )

        # Parse product - should not raise exception
        result = scraper.parse_product("https://example.com/test")

        # Verify result (should work despite GCS failure)
        assert result["product_slug"] == "paperCoasters"
        assert result["name"] == "Test Product Name"
        assert result["url"] == "https://example.com/test"

    @pytest.mark.integration
    @patch("app.services.vistaprint_scraper.requests.get")
    def test_force_refresh_parameter_passed_to_gcs(
        self, mock_get, mock_gcs_service, mock_html_content
    ):
        """Test that force_refresh parameter is correctly passed to GCS service."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.text = mock_html_content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        scraper = VistaPrintScraper(
            url="https://example.com/test",
            mode=ScrapingMode.SCRAPE,
            force_refresh=False,  # Set to False
            gcs_service=mock_gcs_service,
        )

        # Parse product
        scraper.parse_product("https://example.com/test")

        # Verify force_refresh was passed correctly
        call_args = mock_gcs_service.save_html.call_args
        assert call_args[1]["force_refresh"] is False

    @pytest.mark.integration
    def test_scraper_modes_with_gcs(self, mock_gcs_service):
        """Test different scraper modes with GCS service."""
        modes = [ScrapingMode.SCRAPE, ScrapingMode.MOCK, ScrapingMode.RANDOM]

        for mode in modes:
            scraper = VistaPrintScraper(
                url="https://example.com/test",
                mode=mode,
                force_refresh=True,
                gcs_service=mock_gcs_service,
            )

            assert scraper.mode == mode
            assert scraper.gcs_service is not None

    @pytest.mark.integration
    def test_gcs_service_methods_available(self, mock_gcs_service):
        """Test that GCS service has required methods."""
        required_methods = [
            "save_html",
            "save_image",
            "save_logs",
            "download_image",
            "list_product_images",
            "delete_old_files",
        ]

        for method_name in required_methods:
            assert hasattr(mock_gcs_service, method_name)
            assert callable(getattr(mock_gcs_service, method_name))

    @pytest.mark.integration
    def test_scraper_logging_with_gcs(self, mock_gcs_service):
        """Test that scraper logs GCS integration status."""
        with patch("app.services.vistaprint_scraper.logger") as mock_logger:
            scraper = VistaPrintScraper(
                url="https://example.com/test",
                mode=ScrapingMode.SCRAPE,
                force_refresh=True,
                gcs_service=mock_gcs_service,
            )

            # Verify logging
            mock_logger.info.assert_called()
            log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("gcs_service: True" in call for call in log_calls)

    @pytest.mark.integration
    def test_scraper_logging_without_gcs(self):
        """Test that scraper logs when GCS is not available."""
        with patch("app.services.vistaprint_scraper.logger") as mock_logger:
            scraper = VistaPrintScraper(
                url="https://example.com/test",
                mode=ScrapingMode.SCRAPE,
                force_refresh=False,
            )

            # Verify logging
            mock_logger.info.assert_called()
            log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("gcs_service: False" in call for call in log_calls)
