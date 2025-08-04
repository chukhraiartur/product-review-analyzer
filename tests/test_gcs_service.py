"""Unit tests for Google Cloud Storage service."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from app.services.gcs_service import GCSService


class TestGCSService:
    """Test cases for GCSService."""

    @pytest.fixture
    def mock_gcs_client(self):
        """Mock GCS client."""
        with patch("app.services.gcs_service.storage.Client") as mock_client:
            mock_bucket = Mock()
            mock_client.from_service_account_json.return_value.bucket.return_value = (
                mock_bucket
            )
            yield mock_client

    @pytest.fixture
    def gcs_service(self, mock_gcs_client):
        """Create GCSService instance with mocked client."""
        with patch("app.services.gcs_service.settings") as mock_settings:
            mock_settings.gcp_credentials_path = "./test-credentials.json"
            mock_settings.gcp_bucket_name = "test-bucket"
            service = GCSService()
            yield service

    def test_init(self, mock_gcs_client):
        """Test GCSService initialization."""
        with patch("app.services.gcs_service.settings") as mock_settings:
            mock_settings.gcp_credentials_path = "./test-credentials.json"
            mock_settings.gcp_bucket_name = "test-bucket"

            service = GCSService()

            assert service.bucket is not None
            mock_gcs_client.from_service_account_json.assert_called_once_with(
                "./test-credentials.json"
            )

    def test_get_date_path(self, gcs_service):
        """Test date path generation."""
        date_path = gcs_service._get_date_path()
        now = datetime.now()
        expected = f"year={now.year}/month={now.month:02d}/day={now.day:02d}"
        assert date_path == expected

    def test_get_timestamp(self, gcs_service):
        """Test timestamp generation."""
        timestamp = gcs_service._get_timestamp()
        # Should be in format YYYYMMDD_HHMMSS
        assert len(timestamp) == 15
        assert timestamp[8] == "_"
        assert timestamp.isdigit() or timestamp.replace("_", "").isdigit()

    @patch("app.services.gcs_service.get_logger")
    def test_save_html_success(self, mock_logger, gcs_service):
        """Test successful HTML saving."""
        mock_blob = Mock()
        gcs_service.bucket.blob.return_value = mock_blob

        result = gcs_service.save_html(
            "test-product", "<html>test</html>", force_refresh=True
        )

        assert result is not None
        assert "test-product" in result
        assert ".html" in result
        mock_blob.upload_from_string.assert_called_once()

    @patch("app.services.gcs_service.get_logger")
    def test_save_html_exception(self, mock_logger, gcs_service):
        """Test HTML saving with exception."""
        gcs_service.bucket.blob.side_effect = Exception("Test error")

        result = gcs_service.save_html("test-product", "<html>test</html>")

        assert result is None

    def test_get_image_extension_jpg(self, gcs_service):
        """Test image extension detection for JPEG."""
        jpg_data = b"\xff\xd8\xff\xe0\x00\x10JFIF"
        extension = gcs_service._get_image_extension(jpg_data)
        assert extension == ".jpg"

    def test_get_image_extension_png(self, gcs_service):
        """Test image extension detection for PNG."""
        png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        extension = gcs_service._get_image_extension(png_data)
        assert extension == ".png"

    def test_get_image_extension_unknown(self, gcs_service):
        """Test image extension detection for unknown format."""
        unknown_data = b"unknown format data"
        extension = gcs_service._get_image_extension(unknown_data)
        assert extension == ".jpg"  # Default fallback

    def test_get_content_type(self, gcs_service):
        """Test content type mapping."""
        assert gcs_service._get_content_type(".jpg") == "image/jpeg"
        assert gcs_service._get_content_type(".png") == "image/png"
        assert gcs_service._get_content_type(".gif") == "image/gif"
        assert gcs_service._get_content_type(".unknown") == "image/jpeg"  # Default

    @patch("app.services.gcs_service.get_logger")
    def test_save_image_success(self, mock_logger, gcs_service):
        """Test successful image saving."""
        mock_blob = Mock()
        mock_blob.exists.return_value = False
        gcs_service.bucket.blob.return_value = mock_blob

        image_data = b"\xff\xd8\xff\xe0\x00\x10JFIF"  # JPEG data

        result = gcs_service.save_image("test-product", "123", 1, image_data)

        assert result is not None
        assert "test-product" in result
        assert "123_1" in result
        mock_blob.upload_from_string.assert_called_once()

    @patch("app.services.gcs_service.get_logger")
    def test_save_image_already_exists(self, mock_logger, gcs_service):
        """Test image saving when file already exists."""
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        gcs_service.bucket.blob.return_value = mock_blob

        image_data = b"\xff\xd8\xff\xe0\x00\x10JFIF"

        result = gcs_service.save_image("test-product", "123", 1, image_data)

        assert result is not None
        assert "test-product" in result
        mock_blob.upload_from_string.assert_not_called()

    @patch("app.services.gcs_service.get_logger")
    def test_save_logs_success(self, mock_logger, gcs_service):
        """Test successful log saving."""
        mock_blob = Mock()
        gcs_service.bucket.blob.return_value = mock_blob

        result = gcs_service.save_logs("Test log content")

        assert result is not None
        assert "logs" in result
        assert ".txt" in result
        mock_blob.upload_from_string.assert_called_once()

    @patch("requests.get")
    def test_download_image_success(self, mock_get, gcs_service):
        """Test successful image download."""
        mock_response = Mock()
        mock_response.content = b"image data"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = gcs_service.download_image("http://example.com/image.jpg")

        assert result == b"image data"
        mock_get.assert_called_once_with("http://example.com/image.jpg", timeout=30)

    @patch("requests.get")
    def test_download_image_failure(self, mock_get, gcs_service):
        """Test image download failure."""
        mock_get.side_effect = Exception("Download failed")

        result = gcs_service.download_image("http://example.com/image.jpg")

        assert result is None

    def test_list_product_images(self, gcs_service):
        """Test listing product images."""
        mock_blob1 = Mock()
        mock_blob1.name = "images/test-product/image1.jpg"
        mock_blob2 = Mock()
        mock_blob2.name = "images/test-product/image2.png"

        gcs_service.client.list_blobs.return_value = [mock_blob1, mock_blob2]

        result = gcs_service.list_product_images("test-product")

        assert len(result) == 2
        assert all("test-product" in url for url in result)
        gcs_service.client.list_blobs.assert_called_once_with(
            gcs_service.bucket, prefix="images/test-product/"
        )

    def test_delete_old_files(self, gcs_service):
        """Test deletion of old files."""
        mock_blob_old = Mock()
        mock_blob_old.time_created = datetime.now() - timedelta(days=31)
        mock_blob_old.name = "old_file.txt"

        mock_blob_new = Mock()
        mock_blob_new.time_created = datetime.now() - timedelta(days=5)
        mock_blob_new.name = "new_file.txt"

        gcs_service.client.list_blobs.return_value = [mock_blob_old, mock_blob_new]

        result = gcs_service.delete_old_files(days_old=30)

        assert result == 1
        mock_blob_old.delete.assert_called_once()
        mock_blob_new.delete.assert_not_called()

    @patch("app.services.gcs_service.get_logger")
    def test_get_recent_html_within_24h(self, mock_logger, gcs_service):
        """Test getting recent HTML within 24 hours."""
        # Create mock blob with recent timestamp
        mock_blob = Mock()
        mock_blob.name = (
            "html/year=2025/month=08/day=04/test-product_20250804_120000.html"
        )

        gcs_service.client.list_blobs.return_value = [mock_blob]

        result = gcs_service._get_recent_html("test-product")

        assert result is not None
        assert "test-product" in result

    @patch("app.services.gcs_service.get_logger")
    def test_get_recent_html_old_file(self, mock_logger, gcs_service):
        """Test getting recent HTML with old file (should return None)."""
        # Create mock blob with old timestamp (more than 24 hours)
        mock_blob = Mock()
        mock_blob.name = (
            "html/year=2024/month=01/day=01/test-product_20240101_120000.html"
        )

        gcs_service.client.list_blobs.return_value = [mock_blob]

        result = gcs_service._get_recent_html("test-product")

        assert result is None

    @patch("app.services.gcs_service.get_logger")
    def test_get_recent_html_no_files(self, mock_logger, gcs_service):
        """Test getting recent HTML when no files exist."""
        gcs_service.client.list_blobs.return_value = []

        result = gcs_service._get_recent_html("test-product")

        assert result is None
