"""Storage service for Google Cloud Storage with local fallback."""

import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
from google.cloud import storage  # type: ignore
from google.cloud.exceptions import GoogleCloudError

from app.core.config import settings
from app.core.exceptions import StorageException

logger = logging.getLogger(__name__)


class StorageService:
    """Service for storing files in Google Cloud Storage with local fallback."""

    def __init__(self) -> None:
        """Initialize the storage service."""
        self.use_gcp = self._check_gcp_config()
        self.local_storage_path = Path("./data/storage")

        if self.use_gcp:
            self._init_gcp_client()
        else:
            self._init_local_storage()

    def _check_gcp_config(self) -> bool:
        """Check if GCP configuration is available."""
        return (
            all(
                [
                    settings.gcp_project_id,
                    settings.gcp_bucket_name,
                    settings.gcp_credentials_path,
                ]
            )
            and settings.gcp_credentials_path is not None
        )

    def _init_gcp_client(self) -> None:
        """Initialize Google Cloud Storage client."""
        try:
            if settings.gcp_credentials_path:
                os.environ[
                    "GOOGLE_APPLICATION_CREDENTIALS"
                ] = settings.gcp_credentials_path
            self.gcp_client = storage.Client(project=settings.gcp_project_id)

            self.bucket = self.gcp_client.bucket(settings.gcp_bucket_name)

            # Test connection
            self.bucket.reload()
            logger.info("Successfully connected to Google Cloud Storage")

        except Exception as e:
            logger.warning(f"Failed to initialize GCP client: {str(e)}")
            logger.info("Falling back to local storage")
            self.use_gcp = False
            self._init_local_storage()

    def _init_local_storage(self) -> None:
        """Initialize local storage directory."""
        try:
            self.local_storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using local storage at: {self.local_storage_path}")

        except Exception as e:
            logger.error(f"Failed to initialize local storage: {str(e)}")
            raise StorageException("Failed to initialize storage", str(e))

    def upload_image(self, image_url: str, filename: Optional[str] = None) -> str:
        """
        Upload image from URL to storage.

        Args:
            image_url: URL of the image to upload
            filename: Optional custom filename

        Returns:
            Storage path/URL of the uploaded image
        """
        try:
            # Download image from URL
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            # Generate filename if not provided
            if not filename:
                filename = self._generate_filename(image_url)

            # Upload to storage
            if self.use_gcp:
                return self._upload_to_gcp(response.content, filename)
            else:
                return self._upload_to_local(response.content, filename)

        except requests.RequestException as e:
            logger.error(f"Failed to download image from {image_url}: {str(e)}")
            raise StorageException(f"Failed to download image from {image_url}", str(e))

        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            raise StorageException("Failed to upload image", str(e))

    def upload_file(self, file_path: str, filename: Optional[str] = None) -> str:
        """
        Upload local file to storage.

        Args:
            file_path: Path to the local file
            filename: Optional custom filename

        Returns:
            Storage path/URL of the uploaded file
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Generate filename if not provided
            if not filename:
                filename = os.path.basename(file_path)

            # Read file content
            with open(file_path, "rb") as f:
                content = f.read()

            # Upload to storage
            if self.use_gcp:
                return self._upload_to_gcp(content, filename)
            else:
                return self._upload_to_local(content, filename)

        except Exception as e:
            logger.error(f"Error uploading file {file_path}: {str(e)}")
            raise StorageException(f"Failed to upload file {file_path}", str(e))

    def download_file(self, storage_path: str, local_path: str) -> None:
        """
        Download file from storage to local path.

        Args:
            storage_path: Storage path/URL of the file
            local_path: Local path to save the file
        """
        try:
            if self.use_gcp:
                self._download_from_gcp(storage_path, local_path)
            else:
                self._download_from_local(storage_path, local_path)

        except Exception as e:
            logger.error(f"Error downloading file {storage_path}: {str(e)}")
            raise StorageException(f"Failed to download file {storage_path}", str(e))

    def delete_file(self, storage_path: str) -> bool:
        """
        Delete file from storage.

        Args:
            storage_path: Storage path/URL of the file to delete

        Returns:
            True if file was deleted, False otherwise
        """
        try:
            if self.use_gcp:
                return self._delete_from_gcp(storage_path)
            else:
                return self._delete_from_local(storage_path)

        except Exception as e:
            logger.error(f"Error deleting file {storage_path}: {str(e)}")
            return False

    def get_file_url(self, storage_path: str) -> str:
        """
        Get public URL for a file in storage.

        Args:
            storage_path: Storage path of the file

        Returns:
            Public URL of the file
        """
        try:
            if self.use_gcp:
                return self._get_gcp_url(storage_path)
            else:
                return self._get_local_url(storage_path)

        except Exception as e:
            logger.error(f"Error getting file URL for {storage_path}: {str(e)}")
            return storage_path

    def _upload_to_gcp(self, content: bytes, filename: str) -> str:
        """Upload content to Google Cloud Storage."""
        try:
            blob = self.bucket.blob(filename)
            blob.upload_from_string(
                content, content_type=self._get_content_type(filename)
            )

            logger.debug(f"Uploaded {filename} to GCP")
            return f"gs://{settings.gcp_bucket_name}/{filename}"

        except GoogleCloudError as e:
            logger.error(f"GCP upload error: {str(e)}")
            raise StorageException("Failed to upload to GCP", str(e))

    def _upload_to_local(self, content: bytes, filename: str) -> str:
        """Upload content to local storage."""
        try:
            file_path = self.local_storage_path / filename
            with open(file_path, "wb") as f:
                f.write(content)

            logger.debug(f"Uploaded {filename} to local storage")
            return str(file_path)

        except Exception as e:
            logger.error(f"Local upload error: {str(e)}")
            raise StorageException("Failed to upload to local storage", str(e))

    def _download_from_gcp(self, storage_path: str, local_path: str) -> None:
        """Download file from Google Cloud Storage."""
        try:
            # Extract blob name from GCS path
            blob_name = storage_path.replace(f"gs://{settings.gcp_bucket_name}/", "")
            blob = self.bucket.blob(blob_name)

            blob.download_to_filename(local_path)
            logger.debug(f"Downloaded {storage_path} to {local_path}")

        except GoogleCloudError as e:
            logger.error(f"GCP download error: {str(e)}")
            raise StorageException("Failed to download from GCP", str(e))

    def _download_from_local(self, storage_path: str, local_path: str) -> None:
        """Download file from local storage."""
        try:
            shutil.copy2(storage_path, local_path)
            logger.debug(f"Downloaded {storage_path} to {local_path}")

        except Exception as e:
            logger.error(f"Local download error: {str(e)}")
            raise StorageException("Failed to download from local storage", str(e))

    def _delete_from_gcp(self, storage_path: str) -> bool:
        """Delete file from Google Cloud Storage."""
        try:
            blob_name = storage_path.replace(f"gs://{settings.gcp_bucket_name}/", "")
            blob = self.bucket.blob(blob_name)
            blob.delete()

            logger.debug(f"Deleted {storage_path} from GCP")
            return True

        except GoogleCloudError as e:
            logger.error(f"GCP delete error: {str(e)}")
            return False

    def _delete_from_local(self, storage_path: str) -> bool:
        """Delete file from local storage."""
        try:
            if os.path.exists(storage_path):
                os.remove(storage_path)
                logger.debug(f"Deleted {storage_path} from local storage")
                return True
            return False

        except Exception as e:
            logger.error(f"Local delete error: {str(e)}")
            return False

    def _get_gcp_url(self, storage_path: str) -> str:
        """Get public URL for GCP file."""
        try:
            blob_name = storage_path.replace(f"gs://{settings.gcp_bucket_name}/", "")
            blob = self.bucket.blob(blob_name)
            return blob.public_url

        except GoogleCloudError as e:
            logger.error(f"GCP URL error: {str(e)}")
            return storage_path

    def _get_local_url(self, storage_path: str) -> str:
        """Get local URL for file."""
        return f"file://{storage_path}"

    def _generate_filename(self, image_url: str) -> str:
        """Generate unique filename from image URL."""
        parsed_url = urlparse(image_url)
        original_filename = os.path.basename(parsed_url.path)

        if not original_filename or "." not in original_filename:
            original_filename = "image.jpg"

        # Add timestamp to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(original_filename)

        return f"{name}_{timestamp}{ext}"

    def _get_content_type(self, filename: str) -> str:
        """Get content type based on file extension."""
        ext = os.path.splitext(filename)[1].lower()

        content_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".json": "application/json",
        }

        return content_types.get(ext, "application/octet-stream")

    def get_storage_info(self) -> dict:
        """Get storage service information."""
        return {
            "storage_type": "gcp" if self.use_gcp else "local",
            "bucket_name": settings.gcp_bucket_name if self.use_gcp else None,
            "local_path": str(self.local_storage_path) if not self.use_gcp else None,
            "project_id": settings.gcp_project_id if self.use_gcp else None,
        }
