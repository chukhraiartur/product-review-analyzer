"""Product-related API endpoints."""

import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_data_service,
    get_database,
    get_vistaprint_scraper_service,
)
from app.core.exceptions import ScrapingException
from app.core.logging import get_logger
from app.schemas import (
    ProductResponse,
    ReviewResponse,
    ScrapingRequest,
    ScrapingResponse,
)
from app.services.data_service import DataService
from app.services.vistaprint_scraper import ScrapingMode, VistaPrintScraper

logger = get_logger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/scrape", response_model=ScrapingResponse)
async def scrape_product(
    request: ScrapingRequest,
    db: Session = Depends(get_database),
    vistaprint_scraper: VistaPrintScraper = Depends(get_vistaprint_scraper_service),
    data_service: DataService = Depends(get_data_service),
) -> ScrapingResponse:
    """
    Scrape product reviews from VistaPrint.

    Args:
        request: Scraping request parameters
        db: Database session
        vistaprint_scraper: VistaPrint scraper service
        data_service: Data service

    Returns:
        Scraping response with results
    """
    try:
        logger.info(f"Starting product scraping for URL: {request.url}")
        start_time = time.time()

        # Initialize scraper with request parameters
        scraper = VistaPrintScraper(
            url=request.url,
            mode=ScrapingMode(request.mode),
            force_refresh=request.force_refresh or False,
            gcs_service=vistaprint_scraper.gcs_service,
        )

        # Scrape product data
        vistaprint_product = scraper.get_product_info()

        # Save to database
        product = data_service.save_vistaprint_product(vistaprint_product)

        # Get statistics
        stats = data_service.get_product_statistics(product.id)

        processing_time = time.time() - start_time

        logger.info(
            f"Successfully scraped product {product.id} with {stats['total_reviews']} reviews "
            f"in {processing_time:.2f} seconds"
        )

        return ScrapingResponse(
            product_id=product.id,
            product_title=product.title,
            total_reviews=stats["total_reviews"],
            total_images=stats["total_images"],
            processing_time=processing_time,
            status="completed",
        )

    except ScrapingException as e:
        logger.error(f"Scraping error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Scraping failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during scraping: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during scraping",
        )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    data_service: DataService = Depends(get_data_service),
) -> ProductResponse:
    """
    Get product details with reviews.

    Args:
        product_id: Product ID
        data_service: Data service

    Returns:
        Product response with reviews
    """
    try:
        logger.info(f"Getting product details for ID: {product_id}")

        product = data_service.get_product_with_reviews(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

        # Get statistics
        stats = data_service.get_product_statistics(product_id)

        # Convert reviews to response format
        reviews_response = []
        for review in product.reviews:
            review_response = ReviewResponse(
                id=review.id,
                product_id=review.product_id,
                external_id=review.external_id,
                title=review.title,
                text=review.text,
                rating=review.rating,
                author=review.author,
                date_posted=review.date_posted,
                is_verified_purchase=review.is_verified_purchase,
                position=review.position,
                sentiment=review.sentiment,
                sentiment_score=review.sentiment_score,
                image_urls=[img.original_url for img in review.images],
                created_at=review.created_at,
                updated_at=review.updated_at,
            )
            reviews_response.append(review_response)

        return ProductResponse(
            id=product.id,
            title=product.title,
            url=product.url,
            source=product.source,
            reviews=reviews_response,
            total_reviews=stats["total_reviews"],
            average_rating=stats["average_rating"],
            sentiment_distribution=stats["sentiment_distribution"],
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/", response_model=list[ProductResponse])
async def list_products(
    data_service: DataService = Depends(get_data_service),
) -> list[ProductResponse]:
    """
    Get all products.

    Args:
        data_service: Data service

    Returns:
        List of products
    """
    try:
        logger.info("Getting all products")

        products = data_service.get_all_products()
        products_response = []

        for product in products:
            stats = data_service.get_product_statistics(product.id)

            product_response = ProductResponse(
                id=product.id,
                title=product.title,
                url=product.url,
                source=product.source,
                reviews=[],  # Don't include reviews in list view
                total_reviews=stats["total_reviews"],
                average_rating=stats["average_rating"],
                sentiment_distribution=stats["sentiment_distribution"],
                created_at=product.created_at,
                updated_at=product.updated_at,
            )
            products_response.append(product_response)

        return products_response

    except Exception as e:
        logger.error(f"Error listing products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
