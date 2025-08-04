"""Web scraping service for extracting product reviews."""

import logging
import time
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from app.core.config import settings
from app.core.exceptions import ScrapingException
from app.schemas import ReviewCreate

logger = logging.getLogger(__name__)


class WebScraper:
    """Web scraper for extracting product reviews and images."""

    def __init__(self) -> None:
        """Initialize the web scraper."""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )
        self.timeout = settings.request_timeout
        self.max_retries = settings.max_retries

    def scrape_product_reviews(
        self, url: str, product_id: Optional[str] = None, max_pages: int = 1
    ) -> tuple[str, list[ReviewCreate], list[str]]:
        """
        Scrape product reviews from the given URL.

        Args:
            url: URL to scrape
            product_id: Custom product ID (optional)
            max_pages: Maximum number of pages to scrape

        Returns:
            Tuple of (product_id, reviews, image_urls)
        """
        try:
            logger.info(f"Starting to scrape reviews from: {url}")
            start_time = time.time()

            # Get product information
            product_info = self._get_product_info(url)
            if not product_id:
                product_id = self._generate_product_id(url, product_info["title"])

            reviews: list[ReviewCreate] = []
            all_image_urls: list[str] = []

            # Scrape reviews from multiple pages
            for page in range(1, max_pages + 1):
                page_url = self._get_page_url(url, page)
                logger.info(f"Scraping page {page}: {page_url}")

                page_reviews, page_images = self._scrape_page_reviews(
                    page_url, product_id
                )
                reviews.extend(page_reviews)
                all_image_urls.extend(page_images)

                # Add delay between requests to be respectful
                if page < max_pages:
                    time.sleep(1)

            processing_time = time.time() - start_time
            logger.info(
                f"Scraping completed. Found {len(reviews)} reviews and {len(all_image_urls)} images "
                f"in {processing_time:.2f} seconds"
            )

            return product_id, reviews, all_image_urls

        except Exception as e:
            logger.error(f"Error scraping reviews from {url}: {str(e)}")
            raise ScrapingException(f"Failed to scrape reviews from {url}", str(e))

    def _get_product_info(self, url: str) -> dict[str, str]:
        """Extract product information from the page."""
        try:
            response = self._make_request(url)
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract product title (adjust selectors based on target website)
            title = self._extract_title(soup)
            description = self._extract_description(soup)

            return {"title": title, "description": description or "", "url": url}

        except Exception as e:
            logger.error(f"Error extracting product info: {str(e)}")
            raise ScrapingException("Failed to extract product information", str(e))

    def _scrape_page_reviews(
        self, url: str, product_id: str
    ) -> tuple[list[ReviewCreate], list[str]]:
        """Scrape reviews from a single page."""
        try:
            response = self._make_request(url)
            soup = BeautifulSoup(response.content, "html.parser")

            reviews: list[ReviewCreate] = []
            image_urls: list[str] = []

            # Find review containers (adjust selector based on target website)
            review_containers = soup.find_all("div", class_="review-container")

            for container in review_containers:
                review_data = self._extract_review_data(container)
                if review_data:
                    review = ReviewCreate(
                        product_id=product_id,
                        title=review_data.get("title"),
                        text=review_data["text"],
                        rating=review_data.get("rating"),
                        author=review_data.get("author"),
                        date_posted=review_data.get("date"),
                        is_verified_purchase=review_data.get(
                            "is_verified_purchase", False
                        ),
                        position=review_data.get("position"),
                        external_id=review_data.get("external_id"),
                        image_urls=review_data.get("image_urls", []),
                    )
                    reviews.append(review)
                    image_urls.extend(review_data.get("image_urls", []))

            return reviews, image_urls

        except Exception as e:
            logger.error(f"Error scraping page reviews: {str(e)}")
            raise ScrapingException("Failed to scrape page reviews", str(e))

    def _extract_review_data(self, container) -> Optional[dict]:
        """Extract review data from a review container."""
        try:
            # Extract review text
            text_elem = container.find("div", class_="review-text")
            if not text_elem:
                return None

            text = text_elem.get_text(strip=True)
            if not text:
                return None

            # Extract rating
            rating = None
            rating_elem = container.find("span", class_="rating")
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                try:
                    rating = int(rating_text.split()[0])
                except (ValueError, IndexError):
                    pass

            # Extract author
            author = None
            author_elem = container.find("span", class_="author")
            if author_elem:
                author = author_elem.get_text(strip=True)

            # Extract date
            date = None
            date_elem = container.find("span", class_="date")
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                try:
                    date = datetime.strptime(date_text, "%Y-%m-%d")
                except ValueError:
                    pass

            # Extract image URLs
            image_urls = []
            img_elements = container.find_all("img", class_="review-image")
            for img in img_elements:
                src = img.get("src")
                if src:
                    image_urls.append(src)

            return {
                "text": text,
                "rating": rating,
                "author": author,
                "date": date,
                "image_urls": image_urls,
            }

        except Exception as e:
            logger.error(f"Error extracting review data: {str(e)}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract product title from the page."""
        # Try multiple selectors for title
        title_selectors = ["h1.product-title", "h1.title", ".product-name h1", "h1"]

        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title:
                    return title

        return "Unknown Product"

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product description from the page."""
        desc_selectors = [
            ".product-description",
            ".description",
            "meta[name='description']",
        ]

        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                if selector == "meta[name='description']":
                    content = desc_elem.get("content")
                    if isinstance(content, str):
                        return content if content else None
                    elif content is not None:
                        return str(content)
                    return None
                else:
                    return desc_elem.get_text(strip=True)

        return None

    def _make_request(self, url: str) -> requests.Response:
        """Make HTTP request with retry logic."""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response

            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise ScrapingException(
                        f"Failed to fetch {url} after {self.max_retries} attempts",
                        str(e),
                    )

                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}"
                )
                time.sleep(2**attempt)  # Exponential backoff

        # This should never be reached, but mypy needs it
        raise ScrapingException(
            f"Failed to fetch {url} after {self.max_retries} attempts", "Unknown error"
        )

    def _get_page_url(self, base_url: str, page: int) -> str:
        """Generate URL for a specific page."""
        if page == 1:
            return base_url

        # Add page parameter to URL
        parsed = urlparse(base_url)
        query_params = parsed.query.split("&") if parsed.query else []

        # Remove existing page parameter if present
        query_params = [
            param for param in query_params if not param.startswith("page=")
        ]

        # Add new page parameter
        query_params.append(f"page={page}")

        new_query = "&".join(query_params)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"

    def _generate_product_id(self, url: str, title: str) -> str:
        """Generate a unique product ID based on URL and title."""
        import hashlib

        # Create a hash from URL and title
        content = f"{url}:{title}".encode()
        hash_obj = hashlib.md5(content)
        return hash_obj.hexdigest()[:16]
