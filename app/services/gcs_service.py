"""Google Cloud Storage service for managing files."""

import os
from datetime import UTC, datetime
from typing import Optional

from google.cloud import storage  # type: ignore

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class GCSService:
    """Google Cloud Storage service for file operations."""

    def __init__(self) -> None:
        """Initialize GCS service."""
        if settings.gcp_credentials_path:
            self.client = storage.Client.from_service_account_json(
                settings.gcp_credentials_path
            )
        else:
            # Fallback to default credentials (for local development)
            self.client = storage.Client()

        self.bucket = self.client.bucket(settings.gcp_bucket_name)
        logger.info(f"GCS service initialized with bucket: {settings.gcp_bucket_name}")

    def _get_date_path(self) -> str:
        """Get current date path in format year=YYYY/month=MM/day=DD."""
        now = datetime.now()
        return f"year={now.year}/month={now.month:02d}/day={now.day:02d}"

    def _get_timestamp(self) -> str:
        """Get current timestamp in format YYYYMMDD_HHMMSS."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def save_html(
        self, product_slug: str, html_content: str, force_refresh: bool = False
    ) -> Optional[str]:
        """
        Save HTML content to GCS.

        Args:
            product_slug: Product slug from VistaPrint
            html_content: HTML content to save
            force_refresh: If True, always save new HTML

        Returns:
            GCS URL of saved HTML file or None if failed
        """
        try:
            date_path = self._get_date_path()
            timestamp = self._get_timestamp()
            filename = f"{product_slug}_{timestamp}.html"
            blob_path = f"html/{date_path}/{filename}"

            # Check if recent HTML exists (within 24 hours)
            if not force_refresh:
                existing_html = self._get_recent_html(product_slug)
                if existing_html:
                    logger.info(
                        f"Using existing HTML for {product_slug}: {existing_html}"
                    )
                    return existing_html

            # Save new HTML
            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(html_content, content_type="text/html")

            gcs_url = (
                f"https://storage.googleapis.com/{settings.gcp_bucket_name}/{blob_path}"
            )
            logger.info(f"Saved HTML for {product_slug}: {gcs_url}")
            return gcs_url

        except Exception as e:
            logger.error(f"Failed to save HTML for {product_slug}: {str(e)}")
            return None

    def _get_recent_html(self, product_slug: str) -> Optional[str]:
        """
        Get most recent HTML file for product within 24 hours.

        Args:
            product_slug: Product slug to search for

        Returns:
            GCS URL of recent HTML file or None if not found
        """
        try:
            # List all HTML files for this product
            blobs = self.client.list_blobs(self.bucket, prefix="html/", delimiter="/")

            recent_files = []
            for blob in blobs:
                if blob.name.endswith(".html") and product_slug in blob.name:
                    # Extract timestamp from filename
                    filename = os.path.basename(blob.name)
                    if filename.startswith(f"{product_slug}_"):
                        timestamp_str = filename.replace(
                            f"{product_slug}_", ""
                        ).replace(".html", "")
                        try:
                            file_time = datetime.strptime(
                                timestamp_str, "%Y%m%d_%H%M%S"
                            )
                            # Check if within 24 hours
                            if (datetime.now() - file_time).total_seconds() < 24 * 3600:
                                recent_files.append((file_time, blob))
                        except ValueError:
                            continue

            if recent_files:
                # Get most recent file
                recent_files.sort(key=lambda x: x[0], reverse=True)
                most_recent_blob = recent_files[0][1]
                gcs_url = f"https://storage.googleapis.com/{settings.gcp_bucket_name}/{most_recent_blob.name}"
                return gcs_url

        except Exception as e:
            logger.error(f"Failed to get recent HTML for {product_slug}: {str(e)}")

        return None

    def save_image(
        self, product_slug: str, external_id: str, image_order: int, image_data: bytes
    ) -> Optional[str]:
        """
        Save image to GCS.

        Args:
            product_slug: Product slug
            external_id: Review external ID
            image_order: Order number of image in review
            image_data: Image binary data

        Returns:
            GCS URL of saved image or None if failed
        """
        try:
            # Determine file extension from image data
            file_extension = self._get_image_extension(image_data)
            filename = f"{external_id}_{image_order}{file_extension}"
            blob_path = f"images/{product_slug}/{filename}"

            # Check if image already exists
            blob = self.bucket.blob(blob_path)
            if blob.exists():
                logger.info(f"Image already exists: {blob_path}")
                return f"https://storage.googleapis.com/{settings.gcp_bucket_name}/{blob_path}"

            # Save new image
            content_type = self._get_content_type(file_extension)
            blob.upload_from_string(image_data, content_type=content_type)

            gcs_url = (
                f"https://storage.googleapis.com/{settings.gcp_bucket_name}/{blob_path}"
            )
            logger.info(f"Saved image: {gcs_url}")
            return gcs_url

        except Exception as e:
            logger.error(f"Failed to save image {external_id}_{image_order}: {str(e)}")
            return None

    def _get_image_extension(self, image_data: bytes) -> str:
        """Determine image extension from binary data."""
        # Check for common image signatures
        if image_data.startswith(b"\xff\xd8\xff"):
            return ".jpg"
        elif image_data.startswith(b"\x89PNG\r\n\x1a\n"):
            return ".png"
        elif image_data.startswith(b"GIF87a") or image_data.startswith(b"GIF89a"):
            return ".gif"
        elif image_data.startswith(b"RIFF") and image_data[8:12] == b"WEBP":
            return ".webp"
        else:
            # Default to jpg if unknown
            return ".jpg"

    def _get_content_type(self, file_extension: str) -> str:
        """Get content type for file extension."""
        content_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        return content_types.get(file_extension.lower(), "image/jpeg")

    def save_logs(self, log_content: str) -> Optional[str]:
        """
        Save logs to GCS.

        Args:
            log_content: Log content to save

        Returns:
            GCS URL of saved log file or None if failed
        """
        try:
            date_path = self._get_date_path()
            timestamp = self._get_timestamp()
            filename = f"logs_{timestamp}.txt"
            blob_path = f"logs/{date_path}/{filename}"

            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(log_content, content_type="text/plain")

            gcs_url = (
                f"https://storage.googleapis.com/{settings.gcp_bucket_name}/{blob_path}"
            )
            logger.info(f"Saved logs: {gcs_url}")
            return gcs_url

        except Exception as e:
            logger.error(f"Failed to save logs: {str(e)}")
            return None

    def download_image(self, image_url: str) -> Optional[bytes]:
        """
        Download image from URL and return binary data.

        Args:
            image_url: URL of image to download

        Returns:
            Image binary data or None if failed
        """
        try:
            import requests

            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Failed to download image from {image_url}: {str(e)}")
            return None

    def list_product_images(self, product_slug: str) -> list[str]:
        """
        List all images for a product.

        Args:
            product_slug: Product slug

        Returns:
            List of GCS URLs for product images
        """
        try:
            blobs = self.client.list_blobs(
                self.bucket, prefix=f"images/{product_slug}/"
            )

            image_urls = []
            for blob in blobs:
                gcs_url = f"https://storage.googleapis.com/{settings.gcp_bucket_name}/{blob.name}"
                image_urls.append(gcs_url)

            return image_urls

        except Exception as e:
            logger.error(f"Failed to list images for {product_slug}: {str(e)}")
            return []

    def delete_old_files(self, days_old: int = 30) -> int:
        """
        Delete files older than specified days.

        Args:
            days_old: Delete files older than this many days

        Returns:
            Number of deleted files
        """
        try:

            cutoff_date = datetime.now(UTC).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_old)

            deleted_count = 0
            blobs = self.client.list_blobs(self.bucket)

            for blob in blobs:
                if blob.time_created < cutoff_date:
                    blob.delete()
                    deleted_count += 1
                    logger.info(f"Deleted old file: {blob.name}")

            logger.info(f"Deleted {deleted_count} old files")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to delete old files: {str(e)}")
            return 0
