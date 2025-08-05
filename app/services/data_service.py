"""Data service for managing products and reviews."""

import time
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.database import Product, Review, ReviewImage
from app.schemas import VistaPrintProduct, VistaPrintReview
from app.services.gcs_service import GCSService
from app.services.llm import LLMService
from app.services.vector_db import VectorDBService

logger = get_logger(__name__)


class DataService:
    """Service for managing product and review data."""

    def __init__(
        self,
        db: Session,
        llm_service: LLMService,
        gcs_service: GCSService,
        vector_db_service: VectorDBService,
    ) -> None:
        """
        Initialize the data service.

        Args:
            db: Database session
            llm_service: LLM service for sentiment analysis
            gcs_service: Google Cloud Storage service for images
            vector_db_service: Vector database service for embeddings
        """
        self.db = db
        self.llm_service = llm_service
        self.gcs_service = gcs_service
        self.vector_db_service = vector_db_service

    def save_vistaprint_product(self, vistaprint_product: VistaPrintProduct) -> Product:
        """
        Save VistaPrint product and its reviews to the database.

        Args:
            vistaprint_product: VistaPrint product data

        Returns:
            Saved Product object
        """
        try:
            logger.info(f"Saving VistaPrint product: {vistaprint_product.name}")
            start_time = time.time()

            # Check if product already exists
            existing_product = (
                self.db.query(Product)
                .filter(Product.product_slug == vistaprint_product.product_slug)
                .first()
            )

            if existing_product:
                logger.info(f"Product already exists, updating: {existing_product.id}")
                # Update existing product
                existing_product.title = vistaprint_product.name
                existing_product.url = vistaprint_product.url
                existing_product.updated_at = datetime.utcnow()
                product = existing_product
            else:
                # Create new product
                product = Product(
                    product_slug=vistaprint_product.product_slug,
                    title=vistaprint_product.name,  # Use name as title in DB
                    url=vistaprint_product.url,
                    source="vistaprint",
                )
                self.db.add(product)

            self.db.flush()  # Get the product ID

            # Save reviews
            total_reviews = 0
            total_images = 0

            for vistaprint_review in vistaprint_product.reviews:
                try:
                    review = self._create_review_from_vistaprint(
                        product.id, vistaprint_review
                    )
                    if review:
                        total_reviews += 1
                        total_images += len(vistaprint_review.images)

                        # Save images
                        self._save_review_images(
                            review.id, product.id, vistaprint_review.images
                        )

                except Exception as e:
                    logger.error(
                        f"Error saving review {vistaprint_review.external_id}: {str(e)}"
                    )
                    continue

            self.db.commit()

            processing_time = time.time() - start_time
            action = "updated" if existing_product else "saved"
            logger.info(
                f"Successfully {action} product {product.id} with {total_reviews} reviews "
                f"and {total_images} images in {processing_time:.2f} seconds"
            )

            return product

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving VistaPrint product: {str(e)}")
            raise

    def _create_review_from_vistaprint(
        self, product_id: int, vistaprint_review: VistaPrintReview
    ) -> Optional[Review]:
        """
        Create a Review object from VistaPrint review data.

        Args:
            product_id: Product ID
            vistaprint_review: VistaPrint review data

        Returns:
            Created Review object or None if failed
        """
        try:
            # Check if review already exists
            existing_review = (
                self.db.query(Review)
                .filter(Review.external_id == vistaprint_review.external_id)
                .first()
            )

            if existing_review:
                logger.debug(f"Review already exists: {existing_review.id}")
                return existing_review

            # Parse date if provided
            date_posted = None
            if vistaprint_review.date_posted:
                try:
                    date_posted = datetime.strptime(
                        vistaprint_review.date_posted, "%Y-%m-%d %H:%M:%S"
                    )
                except ValueError:
                    logger.warning(
                        f"Invalid date format: {vistaprint_review.date_posted}"
                    )

            # Create review
            review = Review(
                product_id=product_id,
                external_id=vistaprint_review.external_id,
                title=vistaprint_review.title,
                text=vistaprint_review.description,  # Use description as text in DB
                rating=vistaprint_review.score,
                author=vistaprint_review.author,
                date_posted=date_posted,
                is_verified_purchase=vistaprint_review.is_verified_purchase,
                position=vistaprint_review.position,
            )

            # Analyze sentiment
            try:
                sentiment_result = self.llm_service.analyze_sentiment(
                    vistaprint_review.description
                )
                review.sentiment = sentiment_result["sentiment"]
                review.sentiment_score = sentiment_result["score"]
                logger.debug(
                    f"Sentiment analysis for review {vistaprint_review.external_id}: {sentiment_result['sentiment']}"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to analyze sentiment for review {vistaprint_review.external_id}: {str(e)}"
                )
                # For now, use simple sentiment detection
                text_lower = vistaprint_review.description.lower()
                if any(
                    word in text_lower
                    for word in ["great", "excellent", "amazing", "love", "perfect"]
                ):
                    review.sentiment = "positive"
                    review.sentiment_score = 0.8
                elif any(
                    word in text_lower
                    for word in ["bad", "terrible", "awful", "hate", "worst"]
                ):
                    review.sentiment = "negative"
                    review.sentiment_score = -0.8
                else:
                    review.sentiment = "neutral"
                    review.sentiment_score = 0.0

            self.db.add(review)
            self.db.flush()  # Get the review ID

            # Add to vector database for search
            try:
                self.vector_db_service.add_reviews(
                    [review.id], [vistaprint_review.description]
                )
                logger.debug(f"Added review {review.id} to vector database")
            except Exception as e:
                logger.warning(
                    f"Failed to add review {review.id} to vector database: {str(e)}"
                )

            return review

        except Exception as e:
            logger.error(f"Error creating review from VistaPrint data: {str(e)}")
            return None

    def _save_review_images(
        self, review_id: int, product_id: int, image_urls: list[str]
    ) -> None:
        """
        Save review images to Google Cloud Storage and database.

        Args:
            review_id: Review ID
            product_id: Product ID
            image_urls: List of image URLs
        """
        try:
            for order, image_url in enumerate(image_urls, 1):
                if not image_url:
                    continue

                # Check if image already exists
                existing_image = (
                    self.db.query(ReviewImage)
                    .filter(
                        ReviewImage.original_url == image_url,
                        ReviewImage.review_id == review_id,
                    )
                    .first()
                )

                if existing_image:
                    logger.debug(f"Image already exists: {existing_image.id}")
                    continue

                # Get product slug for GCS path
                product = (
                    self.db.query(Product).filter(Product.id == product_id).first()
                )
                if not product or not product.product_slug:
                    logger.error(
                        f"Product or product_slug not found for product_id: {product_id}"
                    )
                    continue

                # Download image from URL
                image_data = self.gcs_service.download_image(image_url)
                if not image_data:
                    logger.warning(f"Failed to download image: {image_url}")
                    continue

                # Save image to GCS
                gcs_url = self.gcs_service.save_image(
                    product_slug=product.product_slug,
                    external_id=str(review_id),  # Use review_id as external_id
                    image_order=order,
                    image_data=image_data,
                )

                if gcs_url:
                    # Create review image record
                    review_image = ReviewImage(
                        review_id=review_id,
                        product_id=product_id,
                        original_url=image_url,
                        storage_url=gcs_url,
                        filename=f"{review_id}_{order}",
                        storage_path=f"images/{product.product_slug}/{review_id}_{order}",
                        is_downloaded=True,
                    )
                    self.db.add(review_image)
                    logger.info(
                        f"Saved image {order} for review {review_id}: {gcs_url}"
                    )
                else:
                    logger.warning(f"Failed to save image to GCS: {image_url}")

        except Exception as e:
            logger.error(f"Error saving review images: {str(e)}")

    def get_product_with_reviews(self, product_id: int) -> Optional[Product]:
        """
        Get product with all its reviews.

        Args:
            product_id: Product ID

        Returns:
            Product object with reviews or None if not found
        """
        try:
            return self.db.query(Product).filter(Product.id == product_id).first()
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {str(e)}")
            return None

    def get_all_products(self) -> list[Product]:
        """
        Get all products.

        Returns:
            List of Product objects
        """
        try:
            return self.db.query(Product).all()
        except Exception as e:
            logger.error(f"Error getting all products: {str(e)}")
            return []

    def get_reviews_by_sentiment(
        self, sentiment: str, limit: int = 100
    ) -> list[Review]:
        """
        Get reviews filtered by sentiment.

        Args:
            sentiment: Sentiment to filter by
            limit: Maximum number of reviews to return

        Returns:
            List of Review objects
        """
        try:
            return (
                self.db.query(Review)
                .filter(Review.sentiment == sentiment)
                .limit(limit)
                .all()
            )
        except Exception as e:
            logger.error(f"Error getting reviews by sentiment {sentiment}: {str(e)}")
            return []

    def get_product_statistics(self, product_id: int) -> dict:
        """
        Get product statistics.

        Args:
            product_id: Product ID

        Returns:
            Dictionary with product statistics
        """
        try:
            product = self.get_product_with_reviews(product_id)
            if not product:
                return {}

            reviews = product.reviews
            total_reviews = len(reviews)

            if total_reviews == 0:
                return {
                    "total_reviews": 0,
                    "average_rating": None,
                    "sentiment_distribution": {},
                    "total_images": 0,
                }

            # Calculate average rating
            ratings = [r.rating for r in reviews if r.rating is not None]
            average_rating = sum(ratings) / len(ratings) if ratings else None

            # Calculate sentiment distribution
            sentiment_distribution: dict[str, int] = {}
            for review in reviews:
                sentiment = review.sentiment
                sentiment_distribution[sentiment] = (
                    sentiment_distribution.get(sentiment, 0) + 1
                )

            # Count total images
            total_images = sum(len(review.images) for review in reviews)

            return {
                "total_reviews": total_reviews,
                "average_rating": round(average_rating, 2) if average_rating else None,
                "sentiment_distribution": sentiment_distribution,
                "total_images": total_images,
            }

        except Exception as e:
            logger.error(f"Error getting product statistics for {product_id}: {str(e)}")
            return {}
