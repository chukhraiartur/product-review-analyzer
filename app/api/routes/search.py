"""Search endpoints for semantic review search."""

import logging
import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_database, get_vector_db_service
from app.models.database import Review, ReviewImage
from app.schemas import ReviewResponse, SearchRequest, SearchResponse
from app.services.vector_db import VectorDBService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/reviews", response_model=SearchResponse)
async def search_reviews(
    request: SearchRequest,
    db: Session = Depends(get_database),
    vector_db_service: VectorDBService = Depends(get_vector_db_service),
) -> SearchResponse:
    """
    Search for reviews using semantic similarity.

    Args:
        request: Search request with query and filters

    Returns:
        Search results with similar reviews
    """
    start_time = time.time()

    try:
        logger.info(f"Searching for reviews with query: {request.query}")

        # Get product review IDs if filtering by product
        filter_ids = None
        if request.product_id:
            product_reviews = (
                db.query(Review.id)
                .filter(Review.product_id == request.product_id)
                .all()
            )
            filter_ids = [r.id for r in product_reviews]

        # Search in vector database
        search_results = vector_db_service.search_reviews(
            query=request.query, k=request.limit or 10, filter_ids=filter_ids
        )

        # Get full review data from database
        review_responses = []
        for review_id, similarity_score, review_text in search_results:
            review = db.query(Review).filter(Review.id == review_id).first()
            if not review:
                continue

            # Apply sentiment filter if specified
            if request.sentiment and review.sentiment != request.sentiment:
                continue

            # Get image URLs
            images = (
                db.query(ReviewImage).filter(ReviewImage.review_id == review.id).all()
            )
            image_urls = [img.original_url for img in images]

            review_response = ReviewResponse(
                id=review.id,
                product_id=review.product_id,
                title=review.title,
                text=review.text,
                rating=review.rating,
                author=review.author,
                date_posted=review.date_posted,
                is_verified_purchase=review.is_verified_purchase,
                position=review.position,
                external_id=review.external_id,
                sentiment=review.sentiment,
                sentiment_score=review.sentiment_score,
                image_urls=image_urls,
                created_at=review.created_at,
                updated_at=review.updated_at,
            )
            review_responses.append(review_response)

        processing_time = time.time() - start_time

        logger.info(
            f"Found {len(review_responses)} reviews in {processing_time:.2f} seconds"
        )

        return SearchResponse(
            query=request.query,
            results=review_responses,
            total_results=len(review_responses),
            processing_time=processing_time,
        )

    except Exception as e:
        logger.error(f"Error searching reviews: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during search",
        )


@router.get("/reviews", response_model=SearchResponse)
async def search_reviews_get(
    query: str,
    product_id: str | None = None,
    sentiment: str | None = None,
    limit: int = 10,
    db: Session = Depends(get_database),
    vector_db_service: VectorDBService = Depends(get_vector_db_service),
) -> SearchResponse:
    """
    Search for reviews using GET method (for simple queries).

    Args:
        query: Search query
        product_id: Optional product ID filter
        sentiment: Optional sentiment filter
        limit: Maximum number of results

    Returns:
        Search results with similar reviews
    """
    start_time = time.time()

    try:
        logger.info(f"Searching for reviews with query: {query}")

        # Get product review IDs if filtering by product
        filter_ids = None
        if product_id:
            product_reviews = (
                db.query(Review.id).filter(Review.product_id == product_id).all()
            )
            filter_ids = [r.id for r in product_reviews]

        # Search in vector database
        search_results = vector_db_service.search_reviews(
            query=query, k=limit, filter_ids=filter_ids
        )

        # Get full review data from database
        review_responses = []
        for review_id, similarity_score, review_text in search_results:
            review = db.query(Review).filter(Review.id == review_id).first()
            if not review:
                continue

            # Apply sentiment filter if specified
            if sentiment and review.sentiment != sentiment:
                continue

            # Get image URLs
            images = (
                db.query(ReviewImage).filter(ReviewImage.review_id == review.id).all()
            )
            image_urls = [img.original_url for img in images]

            review_response = ReviewResponse(
                id=review.id,
                product_id=review.product_id,
                title=review.title,
                text=review.text,
                rating=review.rating,
                author=review.author,
                date_posted=review.date_posted,
                is_verified_purchase=review.is_verified_purchase,
                position=review.position,
                external_id=review.external_id,
                sentiment=review.sentiment,
                sentiment_score=review.sentiment_score,
                image_urls=image_urls,
                created_at=review.created_at,
                updated_at=review.updated_at,
            )
            review_responses.append(review_response)

        processing_time = time.time() - start_time

        logger.info(
            f"Found {len(review_responses)} reviews in {processing_time:.2f} seconds"
        )

        return SearchResponse(
            query=query,
            results=review_responses,
            total_results=len(review_responses),
            processing_time=processing_time,
        )

    except Exception as e:
        logger.error(f"Error searching reviews: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during search",
        )


@router.get("/stats")
async def get_search_stats(
    vector_db_service: VectorDBService = Depends(get_vector_db_service),
) -> dict:
    """
    Get vector database statistics for search functionality.

    Returns:
        Vector database statistics
    """
    try:
        stats = vector_db_service.get_stats()
        return {
            "vector_database": stats,
            "search_available": stats.get("total_reviews", 0) > 0,
        }

    except Exception as e:
        logger.error(f"Error getting search stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
