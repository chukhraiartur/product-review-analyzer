"""Integration tests for Google Cloud Storage."""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from app.services.gcs_service import GCSService


class TestGCSIntegration:
    """Integration tests for GCS service."""

    @pytest.fixture
    def temp_credentials_file(self):
        """Create temporary credentials file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            # Mock credentials JSON
            f.write(
                """{
                "type": "service_account",
                "project_id": "test-project",
                "private_key_id": "test-key-id",
                "private_key": "-----BEGIN PRIVATE KEY-----\\nMOCK_KEY\\n-----END PRIVATE KEY-----\\n",
                "client_email": "test@test-project.iam.gserviceaccount.com",
                "client_id": "123456789",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test%40test-project.iam.gserviceaccount.com"
            }"""
            )
            temp_file = f.name

        yield temp_file

        # Cleanup
        os.unlink(temp_file)

    @pytest.mark.integration
    @patch("app.services.gcs_service.settings")
    def test_gcs_service_initialization(self, mock_settings, temp_credentials_file):
        """Test GCS service initialization with real credentials file."""
        mock_settings.gcp_credentials_path = temp_credentials_file
        mock_settings.gcp_bucket_name = "test-bucket"

        # This should not raise an exception even with mock credentials
        # because we're testing the initialization logic
        with patch("app.services.gcs_service.storage.Client"):
            service = GCSService()
            assert service is not None

    @pytest.mark.integration
    def test_gcs_date_path_structure(self):
        """Test that date path structure is correct."""
        with patch("app.services.gcs_service.storage.Client"):
            with patch("app.services.gcs_service.settings") as mock_settings:
                mock_settings.gcp_credentials_path = "test.json"
                mock_settings.gcp_bucket_name = "test-bucket"

                service = GCSService()
                date_path = service._get_date_path()

                # Should be in format year=YYYY/month=MM/day=DD
                parts = date_path.split("/")
                assert len(parts) == 3
                assert parts[0].startswith("year=")
                assert parts[1].startswith("month=")
                assert parts[2].startswith("day=")

    @pytest.mark.integration
    def test_gcs_timestamp_format(self):
        """Test that timestamp format is correct."""
        with patch("app.services.gcs_service.storage.Client"):
            with patch("app.services.gcs_service.settings") as mock_settings:
                mock_settings.gcp_credentials_path = "test.json"
                mock_settings.gcp_bucket_name = "test-bucket"

                service = GCSService()
                timestamp = service._get_timestamp()

                # Should be in format YYYYMMDD_HHMMSS
                assert len(timestamp) == 15
                assert timestamp[8] == "_"
                assert timestamp[:8].isdigit()  # Date part
                assert timestamp[9:].isdigit()  # Time part

    @pytest.mark.integration
    def test_image_extension_detection(self):
        """Test image extension detection with real image data."""
        with patch("app.services.gcs_service.storage.Client"):
            with patch("app.services.gcs_service.settings") as mock_settings:
                mock_settings.gcp_credentials_path = "test.json"
                mock_settings.gcp_bucket_name = "test-bucket"

                service = GCSService()

                # Test JPEG
                jpeg_data = (
                    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00"
                )
                assert service._get_image_extension(jpeg_data) == ".jpg"

                # Test PNG
                png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
                assert service._get_image_extension(png_data) == ".png"

                # Test GIF
                gif_data = (
                    b"GIF87a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!"
                )
                assert service._get_image_extension(gif_data) == ".gif"

    @pytest.mark.integration
    def test_content_type_mapping(self):
        """Test content type mapping for different file extensions."""
        with patch("app.services.gcs_service.storage.Client"):
            with patch("app.services.gcs_service.settings") as mock_settings:
                mock_settings.gcp_credentials_path = "test.json"
                mock_settings.gcp_bucket_name = "test-bucket"

                service = GCSService()

                content_types = {
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".png": "image/png",
                    ".gif": "image/gif",
                    ".webp": "image/webp",
                    ".unknown": "image/jpeg",  # Default fallback
                }

                for extension, expected_type in content_types.items():
                    assert service._get_content_type(extension) == expected_type

    @pytest.mark.integration
    @patch("requests.get")
    def test_image_download_integration(self, mock_get):
        """Test image download integration with requests."""
        # Mock successful response
        mock_response = Mock()
        mock_response.content = b"fake_image_data"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with patch("app.services.gcs_service.storage.Client"):
            with patch("app.services.gcs_service.settings") as mock_settings:
                mock_settings.gcp_credentials_path = "test.json"
                mock_settings.gcp_bucket_name = "test-bucket"

                service = GCSService()
                result = service.download_image("http://example.com/test.jpg")

                assert result == b"fake_image_data"
                mock_get.assert_called_once_with(
                    "http://example.com/test.jpg", timeout=30
                )

    @pytest.mark.integration
    @patch("requests.get")
    def test_image_download_failure_integration(self, mock_get):
        """Test image download failure integration."""
        # Mock failed response
        mock_get.side_effect = Exception("Network error")

        with patch("app.services.gcs_service.storage.Client"):
            with patch("app.services.gcs_service.settings") as mock_settings:
                mock_settings.gcp_credentials_path = "test.json"
                mock_settings.gcp_bucket_name = "test-bucket"

                service = GCSService()
                result = service.download_image("http://example.com/test.jpg")

                assert result is None

    @pytest.mark.integration
    def test_gcs_service_methods_exist(self):
        """Test that all expected GCS service methods exist."""
        with patch("app.services.gcs_service.storage.Client"):
            with patch("app.services.gcs_service.settings") as mock_settings:
                mock_settings.gcp_credentials_path = "test.json"
                mock_settings.gcp_bucket_name = "test-bucket"

                service = GCSService()

                # Check that all required methods exist
                required_methods = [
                    "save_html",
                    "save_image",
                    "save_logs",
                    "download_image",
                    "list_product_images",
                    "delete_old_files",
                    "_get_date_path",
                    "_get_timestamp",
                    "_get_image_extension",
                    "_get_content_type",
                    "_get_recent_html",
                ]

                for method_name in required_methods:
                    assert hasattr(
                        service, method_name
                    ), f"Method {method_name} not found"
                    assert callable(
                        getattr(service, method_name)
                    ), f"Method {method_name} is not callable"
