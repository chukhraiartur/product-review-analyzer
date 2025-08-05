"""VistaPrint web scraper service."""

import json
import random
import time
from datetime import datetime
from enum import Enum
from typing import Optional

import requests
from bs4 import BeautifulSoup
from pydantic import ValidationError

from app.core.config import settings
from app.core.exceptions import ScrapingException
from app.core.logging import get_logger
from app.schemas import VistaPrintProduct, VistaPrintReview
from app.services.gcs_service import GCSService

logger = get_logger(__name__)


class ScrapingMode(str, Enum):
    """Scraping mode enumeration."""

    MOCK = "mock"
    SCRAPE = "scrape"
    RANDOM = "random"


class VistaPrintScraper:
    """VistaPrint web scraper for extracting product reviews and images."""

    page_size = 150
    locale = "en-us"
    base_url = "https://www.vistaprint.com"
    search_url = f"{base_url}/search"

    KEYWORDS = ["food storage", "gloves", "bottle", "t-shirt", "jacket"]
    PRODUCT_LINKS = [
        # 250 reviews (2 requests to get all reviews, there are images in reviews)
        "https://www.vistaprint.com/photo-gifts/paper-coasters",
        # 9 reviews (1 request to get all reviews, there are images in reviews)
        "https://www.vistaprint.com/promotional-products/drinkware/sports-water-bottles/yeti-r-rambler-r-water-bottle-18-oz",
        # 6979 reviews (many requests to get all reviews) - COMMENTED OUT: too many reviews
        # "https://www.vistaprint.com/business-cards/glossy",
        # no reviews - COMMENTED OUT: no reviews
        # "https://www.vistaprint.com/clothing-bags/clothing-accessories/touch-screen-gloves-in-pouch",
    ]

    def __init__(
        self,
        url: Optional[str] = None,
        mode: ScrapingMode = ScrapingMode.SCRAPE,
        force_refresh: bool = False,
        gcs_service: Optional[GCSService] = None,
    ) -> None:
        """
        Initialize the VistaPrint scraper.

        Args:
            url: Product URL to scrape
            mode: Scraping mode (mock, scrape, random)
            force_refresh: Force refresh HTML from website (ignore cached version)
            gcs_service: Google Cloud Storage service for caching and storage
        """
        self.url = url
        self.mode = mode
        self.force_refresh = force_refresh
        self.gcs_service = gcs_service
        logger.info(
            f"VistaPrint scraper initialized with mode: {mode}, force_refresh: {force_refresh}, gcs_service: {gcs_service is not None}"
        )

    def get_user_agent(self) -> str:
        """Get user agent string."""
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"

    def get_serp_headers(self) -> dict[str, str]:
        """Get headers for search requests."""
        return self.get_product_headers()

    def get_product_headers(self) -> dict[str, str]:
        """Get headers for product page requests."""
        return {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en",
            "priority": "u=0, i",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": self.get_user_agent(),
        }

    def get_product_reviews_headers(self) -> dict[str, str]:
        """Get headers for product reviews API requests."""
        return {
            "accept": "*/*",
            "accept-language": "en,en-US;q=0.9,ru-RU;q=0.8,ru;q=0.7,uk-UA;q=0.6,uk;q=0.5,ko;q=0.4",
            "origin": "https://www.vistaprint.com",
            "priority": "u=1, i",
            "referer": "https://www.vistaprint.com/",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": self.get_user_agent(),
        }

    def get_product_info(self) -> VistaPrintProduct:
        """
        Get product information based on the current mode.

        Returns:
            VistaPrintProduct object with product and review data

        Raises:
            ScrapingException: If scraping fails
        """
        try:
            logger.info(f"Getting product info with mode: {self.mode}")

            if self.url is None and self.mode == ScrapingMode.RANDOM:
                product_info = self.parse_serp()
            elif self.url is None and self.mode == ScrapingMode.MOCK:
                self.url = random.choice(self.PRODUCT_LINKS)
                logger.info(f"Selected random product URL: {self.url}")
                product_info = self.parse_product(self.url)
            elif self.url is not None and self.mode == ScrapingMode.MOCK:
                product_info = self.parse_product(self.url)
            elif self.url is not None and self.mode == ScrapingMode.SCRAPE:
                product_info = self.parse_product(self.url)
            else:
                raise ScrapingException("Invalid mode and URL combination")

            # Validate product info with Pydantic
            try:
                validated_product = VistaPrintProduct(**product_info)
                logger.info(
                    f"Successfully scraped product: {validated_product.name} with {len(validated_product.reviews)} reviews"
                )
                return validated_product
            except ValidationError as e:
                logger.error(f"Validation error for product data: {e}")
                raise ScrapingException("Invalid product data structure", str(e))

        except Exception as e:
            logger.error(f"Error getting product info: {str(e)}")
            raise ScrapingException("Failed to get product information", str(e))

    def parse_serp(self) -> dict:
        """Parse search results page and select a random product."""
        try:
            logger.info("Parsing search results page")
            serp_response = self.serp_request()
            soup = BeautifulSoup(serp_response.text, "lxml")

            products = soup.select(".product-tile-container")
            if not products:
                logger.warning("No products found in search results")
                raise ScrapingException("No products found in search results")

            random_product = random.choice(products)
            product_link = random_product.select_one(
                'a[data-cy="link-to-product-page-from-name"]'
            )

            if not product_link:
                logger.warning("No product link found")
                raise ScrapingException("No product link found in search results")

            href = product_link.attrs.get("href", "")
            if isinstance(href, str):
                random_product_slug = href.strip()
            else:
                random_product_slug = str(href).strip()
            if not random_product_slug:
                logger.warning("Empty product slug")
                raise ScrapingException("Empty product slug in search results")

            random_product_url = f"{self.base_url}{random_product_slug}"
            logger.info(f"Selected product from SERP: {random_product_url}")

            return self.parse_product(random_product_url)

        except Exception as e:
            logger.error(f"Error parsing SERP: {str(e)}")
            raise ScrapingException("Failed to parse search results", str(e))

    def serp_request(self) -> requests.Response:
        """Make search request."""
        try:
            query = random.choice(self.KEYWORDS)
            logger.info(f"Making search request for query: {query}")

            params = {"query": query}
            response = requests.get(
                self.search_url,
                params=params,
                headers=self.get_serp_headers(),
                timeout=settings.request_timeout,
            )
            response.raise_for_status()
            response.encoding = "utf-8"

            return response

        except requests.RequestException as e:
            logger.error(f"Search request failed: {str(e)}")
            raise ScrapingException("Failed to make search request", str(e))

    def parse_product(self, url: str) -> dict:
        """
        Parse product page and extract reviews.

        Args:
            url: Product URL to parse

        Returns:
            Dictionary with product information and reviews
        """
        try:
            logger.info(f"Parsing product page: {url}")
            product_response = self.product_request(url=url)
            soup = BeautifulSoup(product_response.text, "lxml")

            product_slug = self.get_product_slug(soup)
            if not product_slug:
                logger.error("Could not extract product slug")
                raise ScrapingException("Failed to extract product slug")

            # Save HTML to Google Cloud Storage for caching
            if self.gcs_service:
                try:
                    gcs_url = self.gcs_service.save_html(
                        product_slug=product_slug,
                        html_content=product_response.text,
                        force_refresh=self.force_refresh,
                    )
                    if gcs_url:
                        logger.info(f"Saved HTML to GCS: {gcs_url}")
                    else:
                        logger.warning("Failed to save HTML to GCS")
                except Exception as e:
                    logger.warning(f"Error saving HTML to GCS: {str(e)}")

            product_name = self.get_product_name(soup)
            if not product_name:
                logger.warning("Could not extract product name, using fallback")
                product_name = "Unknown Product"

            reviews = self.parse_product_reviews(soup)

            logger.info(
                f"Successfully parsed product: {product_name} (Slug: {product_slug}) with {len(reviews)} reviews"
            )

            return {
                "product_slug": product_slug,
                "name": product_name,
                "url": url,
                "reviews": reviews,
            }

        except Exception as e:
            logger.error(f"Error parsing product {url}: {str(e)}")
            raise ScrapingException(f"Failed to parse product {url}", str(e))

    def product_request(self, url: str) -> requests.Response:
        """Make product page request."""
        try:
            response = requests.get(
                url=url,
                headers=self.get_product_headers(),
                timeout=settings.request_timeout,
            )
            response.raise_for_status()
            response.encoding = "utf-8"
            return response

        except requests.RequestException as e:
            logger.error(f"Product request failed for {url}: {str(e)}")
            raise ScrapingException(f"Failed to fetch product page {url}", str(e))

    def get_product_name(self, soup: BeautifulSoup) -> str:
        """Extract product name from the page."""
        try:
            title_elem = soup.select_one(".swan-site-main .swan-grid-container h1")
            if title_elem:
                return title_elem.text.strip()
            return ""
        except Exception as e:
            logger.warning(f"Error extracting product name: {str(e)}")
            return ""

    def parse_product_reviews(self, soup: BeautifulSoup) -> list[dict]:
        """Parse product reviews from the page."""
        try:
            if not soup.select("#reviews-details, #reviews-container"):
                logger.warning("No reviews container found on the page")
                return []

            product_slug = self.get_product_slug(soup)
            if not product_slug:
                logger.error("Could not extract product slug for reviews")
                return []

            start_from = 0
            reviews = []

            while True:
                logger.info(f"Fetching reviews starting from {start_from}")
                product_reviews_response = self.product_reviews_request(
                    product_slug=product_slug, start_from=start_from
                )

                try:
                    json_response = json.loads(product_reviews_response.text)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse reviews JSON: {str(e)}")
                    break

                current_page_reviews = self.get_product_reviews(
                    json_response, start_from
                )
                reviews.extend(current_page_reviews)

                pages_total = json_response.get("pagination", {}).get("pagesTotal", 1)
                current_page_number = json_response.get("pagination", {}).get(
                    "currentPageNumber", 1
                )

                logger.info(
                    f"Page {current_page_number}/{pages_total}, found {len(current_page_reviews)} reviews"
                )

                if current_page_number >= pages_total:
                    break

                start_from += self.page_size
                time.sleep(1)  # Be respectful to the server

            logger.info(f"Total reviews collected: {len(reviews)}")
            return reviews

        except Exception as e:
            logger.error(f"Error parsing product reviews: {str(e)}")
            return []

    def get_product_reviews(self, json_response: dict, start_from: int) -> list[dict]:
        """Extract review data from JSON response."""
        try:
            reviews_data = json_response.get("reviews", [])
            reviews = []

            for position, review in enumerate(reviews_data, start=start_from + 1):
                try:
                    review_data = {
                        "position": position,
                        "external_id": str(review.get("id", "")),  # Convert to string
                        "title": review.get("header"),
                        "date_posted": self.get_product_review_date_posted(review),
                        "author": review.get("nickname"),
                        "score": review.get("rating"),
                        "description": review.get("comments", ""),
                        "is_verified_purchase": review.get("isVerifiedBuyer", False),
                        "images": self.get_product_review_images(review),
                    }

                    # Validate review data
                    try:
                        VistaPrintReview(**review_data)
                        reviews.append(review_data)
                    except ValidationError as e:
                        logger.warning(
                            f"Invalid review data at position {position}: {e}"
                        )
                        continue

                except Exception as e:
                    logger.warning(
                        f"Error processing review at position {position}: {str(e)}"
                    )
                    continue

            return reviews

        except Exception as e:
            logger.error(f"Error extracting reviews from JSON: {str(e)}")
            return []

    def get_product_slug(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product slug from the page."""
        try:
            meta_elem = soup.select_one('meta[name="pageName"]')
            if meta_elem:
                content = meta_elem.attrs.get("content", "")
                if isinstance(content, str) and ":" in content:
                    return content.split(":")[0].strip()
                elif isinstance(content, str):
                    return content.strip()
            return None
        except Exception as e:
            logger.warning(f"Error extracting product slug: {str(e)}")
            return None

    def product_reviews_request(
        self, product_slug: str, start_from: int
    ) -> requests.Response:
        """Make product reviews API request."""
        try:
            params = {
                "pageSize": str(self.page_size),
                "sortBy": "Newest",
                "startFrom": str(start_from),
            }

            response = requests.get(
                url=f"https://rating-reviews.prod.merch.vpsvc.com/v1/reviews/vistaprint/{self.locale}/{product_slug}",
                params=params,
                headers=self.get_product_reviews_headers(),
                timeout=settings.request_timeout,
            )
            response.raise_for_status()
            return response

        except requests.RequestException as e:
            logger.error(f"Product reviews request failed: {str(e)}")
            raise ScrapingException("Failed to fetch product reviews", str(e))

    def get_product_review_date_posted(self, review: dict) -> Optional[str]:
        """Extract and format review posting date."""
        try:
            date_posted = review.get("authorSubmissionDate")
            if date_posted:
                parsed_date = datetime.strptime(date_posted, "%b %d, %Y")
                return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
            return None
        except Exception as e:
            logger.warning(f"Error parsing review date: {str(e)}")
            return None

    def get_product_review_images(self, review: dict) -> list[str]:
        """Extract image URLs from review."""
        try:
            images = review.get("images", [])
            image_urls = []

            for img in images:
                if isinstance(img, dict) and img.get("src"):
                    image_urls.append(img["src"])

            return image_urls

        except Exception as e:
            logger.warning(f"Error extracting review images: {str(e)}")
            return []
