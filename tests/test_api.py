"""API endpoint tests."""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Product Review Analyzer API"
    assert data["version"] == "1.0.0"


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "version" in data


def test_health_live(client: TestClient):
    """Test health live endpoint."""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


def test_health_ready(client: TestClient):
    """Test health ready endpoint."""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_products_list_empty(client: TestClient):
    """Test products list endpoint with empty database."""
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_product_not_found(client: TestClient):
    """Test getting non-existent product."""
    response = client.get("/api/v1/products/non-existent-id")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_search_stats(client: TestClient):
    """Test search statistics endpoint."""
    response = client.get("/api/v1/search/stats")
    assert response.status_code == 200
    data = response.json()
    assert "vector_database" in data
    assert "search_available" in data


def test_search_reviews_empty(client: TestClient):
    """Test search reviews endpoint with empty database."""
    response = client.get("/api/v1/search/reviews?query=test")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "test"
    assert data["total_results"] == 0
    assert isinstance(data["results"], list)


def test_scraping_invalid_url(client: TestClient):
    """Test scraping with invalid URL."""
    response = client.post(
        "/api/v1/products/scrape", json={"url": "invalid-url", "max_pages": 1}
    )
    assert response.status_code == 400  # Bad request error


def test_api_docs_available(client: TestClient):
    """Test that API documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_available(client: TestClient):
    """Test that ReDoc documentation is available."""
    response = client.get("/redoc")
    assert response.status_code == 200
