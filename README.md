# Product Review Analyzer

AI-powered product review analysis system with VistaPrint integration, sentiment analysis, and semantic search capabilities.

## 🚀 Features

- **VistaPrint Integration**: Scrape product reviews from VistaPrint with full pagination support
- **AI Sentiment Analysis**: Analyze review sentiment using OpenAI GPT models
- **Vector Database**: Store and search reviews using FAISS for semantic similarity
- **Google Cloud Storage**: Store HTML pages, review images, and logs with intelligent caching
- **RESTful API**: FastAPI-based API with comprehensive documentation
- **Database Management**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Containerization**: Docker and Docker Compose for easy deployment
- **Code Quality**: Black, Ruff, MyPy for code formatting and type checking
- **Testing**: Comprehensive test suite with coverage reporting
- **CI/CD**: GitHub Actions pipeline for automated testing and deployment

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   VistaPrint    │    │   FastAPI       │    │   PostgreSQL    │
│   Scraper       │───▶│   Application   │───▶│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   OpenAI API    │    │   FAISS Vector  │
                       │   (Sentiment)   │    │   Database      │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Google Cloud  │
                       │   Storage       │
                       └─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy
- **Database**: PostgreSQL
- **AI/ML**: OpenAI GPT-4, FAISS, Sentence Transformers
- **Web Scraping**: BeautifulSoup, Requests
- **Storage**: Google Cloud Storage
- **Containerization**: Docker, Docker Compose
- **Code Quality**: Black, Ruff, MyPy, Poetry
- **Testing**: Pytest, Pytest-Cov, Mock, Integration tests
- **CI/CD**: GitHub Actions

## 📋 Prerequisites

- Docker and Docker Compose
- Google Cloud Platform account (for GCS)
- OpenAI API key
- Git

## 🎯 System Overview

### ✅ **Core Functionality**

1. **Web Scraping**: VistaPrint scraper using BeautifulSoup
2. **Database Storage**: PostgreSQL with SQLAlchemy ORM
3. **Media Storage**: Google Cloud Storage for images
4. **Sentiment Analysis**: OpenAI GPT API integration
5. **Vector Database**: FAISS for semantic search
6. **API Endpoints**: FastAPI with GET/POST endpoints
7. **Docker**: Full containerization
8. **Code Quality**: Clean, tested codebase

### 🔧 **Technical Implementation Details**

#### **Web Scraping (BeautifulSoup)**
- **VistaPrint Integration**: Specialized scraper for VistaPrint product pages
- **Pagination Support**: Handles multiple review pages automatically
- **Data Extraction**: Reviews, ratings, images, verified purchases
- **Error Handling**: Retries, fallbacks, comprehensive logging
- **Caching**: HTML pages cached in Google Cloud Storage

#### **Sentiment Analysis (OpenAI)**
- **Model**: GPT-3.5-turbo for cost-effective analysis
- **Structured Output**: JSON responses with sentiment, confidence, score
- **Fallback System**: Keyword-based analysis when API unavailable
- **Batch Processing**: Efficient handling of multiple reviews
- **Error Recovery**: Graceful degradation on API failures

#### **Vector Database (FAISS)**
- **Embedding Model**: Sentence Transformers (paraphrase-MiniLM-L3-v2)
- **Index Type**: FAISS IndexFlatIP for cosine similarity
- **Semantic Search**: Find similar reviews using vector embeddings
- **Local Storage**: FAISS index stored locally for fast access
- **Metadata Management**: Review IDs and texts stored alongside embeddings

#### **Google Cloud Storage**
- **HTML Caching**: 24-hour cache for product pages
- **Image Storage**: Automatic download and storage of review images
- **Structured Organization**: Date-based folder structure
- **Public Access**: Images publicly accessible for web display
- **Deduplication**: Skip existing images, only download new ones

#### **Database Design (PostgreSQL)**
- **Products Table**: Store product information and metadata
- **Reviews Table**: Store reviews with sentiment analysis results
- **Review Images Table**: Store image URLs and metadata
- **Relationships**: Proper foreign key relationships
- **Indexing**: Optimized for search and retrieval

## ⚠️ Important Notes

### Port Conflicts with Local PostgreSQL

If you have PostgreSQL installed locally on your system, it might conflict with the Docker container. The default PostgreSQL port is 5432.

**Symptoms of port conflict:**
- Connection timeout or authentication errors
- Error: "FATAL: password authentication failed for user"

**Solution:**
1. Change `DB_PORT=5433` in your `.env` file
2. The Docker container will run on port 5433 instead of 5432
3. Your local PostgreSQL can continue running on port 5432

**To check if port 5432 is already in use:**
```bash
# Windows
netstat -an | findstr :5432

# Linux/Mac
netstat -an | grep :5432
```

## 🚀 Quick Start - Complete Testing Guide

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd product-review-analyzer

# Verify all files are present
ls -la
```

### Step 2: Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# Application settings
DEBUG=false
TESTING=false

# Database settings (PostgreSQL)
DB_HOST=postgres
DB_PORT=5432
DB_USER=review_user
DB_PASSWORD=review_password
DB_NAME=review_analyzer

# OpenAI settings
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Google Cloud Storage settings
GCP_PROJECT_ID=your_gcp_project_id
GCP_BUCKET_NAME=your_gcs_bucket_name
GCP_CREDENTIALS_PATH=./credentials/your_credentials_file.json
GCP_USE_EMULATOR=false
GCP_EMULATOR_HOST=localhost:4443

# Vector database settings
FAISS_INDEX_PATH=./data/faiss_index

# Scraping settings
REQUEST_TIMEOUT=30
MAX_RETRIES=3

# API settings
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 3: Set Up Google Cloud Credentials

1. **Create a Google Cloud Project** (if you don't have one):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Note your Project ID

2. **Enable Google Cloud Storage API**:
   - Go to APIs & Services > Library
   - Search for "Cloud Storage"
   - Enable the "Cloud Storage" API

3. **Create a Service Account**:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Give it a name (e.g., "review-analyzer")
   - Grant "Storage Object Admin" role
   - Create and download the JSON key file

4. **Create a GCS Bucket**:
   - Go to Cloud Storage > Buckets
   - Click "Create Bucket"
   - Choose a unique name (e.g., "product-review-analyzer-data")
   - Choose a location close to you
   - Set access control to "Uniform"

5. **Place Credentials File**:
   - Create a `credentials` folder in the project root
   - Place your downloaded JSON credentials file in the `credentials` folder
   - Update `GCP_CREDENTIALS_PATH` in `.env` to point to your file

### Step 4: Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

### Step 5: Run Pre-Application Tests

Before starting the application, let's verify that the core functionality works:

```bash
# Run tests using the test runner (recommended)
python scripts/run_tests.py mock

# Or run specific test modes:
python scripts/run_tests.py unit        # Unit tests only (fastest)
python scripts/run_tests.py mock        # Unit + mock tests (recommended)
python scripts/run_tests.py all         # All tests (requires real services)

# Or using make commands:
make test-mock                          # Unit + mock tests
make test-unit                          # Unit tests only
make test-all                           # All tests
```

**Expected Results:**
- **Unit tests**: ✅ All should pass (9/9)
- **Mock tests**: ✅ All should pass (26/26)
- **Integration tests**: ⚠️ May fail without real OpenAI/GCS credentials (this is normal)

**Note**: The CI/CD pipeline is configured to run only unit tests and mock tests, so failures in integration tests won't block deployment. Integration tests are designed to run with real external services in the CI/CD environment.

**Test Modes Explained:**
- **Unit Mode**: Fastest, tests core functionality without external dependencies
- **Mock Mode**: Tests API endpoints with mocked external services (recommended for development)
- **All Mode**: Full test suite including integration tests with real services

### Step 6: Start the Application

```bash
# Build and start all services
docker-compose up --build -d

# Check if services are running
docker-compose ps

# Expected output:
# NAME                  IMAGE                         COMMAND                  SERVICE    CREATED       STATUS                    PORTS
# review_analyzer_app   product-review-analyzer-app   "poetry run uvicorn …"   app        5 hours ago   Up 15 seconds (healthy)   0.0.0.0:8000->8000/tcp
# review_analyzer_db    postgres:15-alpine            "docker-entrypoint.s…"   postgres   5 hours ago   Up 26 seconds (healthy)   0.0.0.0:5433->5432/tcp
```

### Step 7: Verify Application Health

```bash
# Check health endpoint
curl http://localhost:8000/api/v1/health/

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-08-05T02:28:42.733312",
  "version": "Product Review Analyzer",
  "database_status": "healthy",
  "vector_db_status": "healthy",
  "storage_status": "healthy"
}
```

### Step 8: Test All API Endpoints

#### 8.1 Test Health and Documentation
```bash
# Health check
curl http://localhost:8000/api/v1/health/

# API documentation
open http://localhost:8000/docs
# or
curl http://localhost:8000/docs

# ReDoc documentation
open http://localhost:8000/redoc
# or
curl http://localhost:8000/redoc
```

#### 8.2 Test Vector Database Search
```bash
# Get search statistics
curl http://localhost:8000/api/v1/search/stats

# Expected response:
{
  "vector_database": {
    "total_reviews": 0,
    "total_vectors": 0,
    "dimension": 384,
    "index_type": "FAISS FlatIP"
  },
  "search_available": false
}

# Test search (should return empty results initially)
curl -X POST "http://localhost:8000/api/v1/search/reviews" \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "k": 5}'

# Expected response:
{
  "query": "test query",
  "results": [],
  "processing_time": 0.123,
  "total_results": 0
}
```

#### 8.3 Test Product Scraping
```bash
# Scrape a product (this will test scraping, sentiment analysis, and vector storage)
curl -X POST "http://localhost:8000/api/v1/products/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.vistaprint.com/promotional-products/drinkware/sports-water-bottles/yeti-r-rambler-r-water-bottle-18-oz",
    "mode": "scrape",
    "force_refresh": false
  }'

# Expected response:
{
  "message": "Product scraping completed successfully",
  "product_id": 1,
  "reviews_count": 25,
  "processing_time": 45.2
}
```

#### 8.4 Test Product Retrieval
```bash
# Get all products
curl http://localhost:8000/api/v1/products/

# Get specific product
curl http://localhost:8000/api/v1/products/1
```

#### 8.5 Test Enhanced Search (after scraping)
```bash
# Get updated search statistics
curl http://localhost:8000/api/v1/search/stats

# Search for reviews with sentiment
curl -X POST "http://localhost:8000/api/v1/search/reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "great quality",
    "k": 5
  }'

# Expected response:
{
  "query": "great quality",
  "results": [
    {
      "review_id": 1,
      "title": "Excellent Product",
      "text": "This is a great quality product...",
      "rating": 5,
      "sentiment": "positive",
      "similarity_score": 0.85
    }
  ],
  "processing_time": 0.234,
  "total_results": 5
}
```

### Step 9: Test Error Handling

```bash
# Test invalid URL
curl -X POST "http://localhost:8000/api/v1/products/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "invalid-url",
    "mode": "scrape",
    "force_refresh": false
  }'

# Expected: 400 Bad Request

# Test non-existent product
curl http://localhost:8000/api/v1/products/999

# Expected: 404 Not Found
```

### Step 10: Run Post-Application Tests

```bash
# Run tests again to ensure everything still works
poetry run pytest tests/ -v

# Run specific test categories
poetry run pytest tests/api/ -v
poetry run pytest tests/unit/ -v
```

### Step 11: Monitor Application Logs

```bash
# View application logs
docker-compose logs -f app

# View database logs
docker-compose logs -f postgres

# View all logs
docker-compose logs -f
```

### Step 12: Clean Shutdown

```bash
# Stop all services gracefully
docker-compose down

# Verify all containers are stopped
docker-compose ps

# Expected: No containers running

# Optional: Remove all data (WARNING: This will delete everything)
docker-compose down -v
```

## Complete Testing Checklist

- [ ] ✅ Repository cloned successfully
- [ ] ✅ Environment variables configured
- [ ] ✅ Google Cloud credentials set up
- [ ] ✅ OpenAI API key configured
- [ ] ✅ Pre-application tests run
- [ ] ✅ Docker containers started successfully
- [ ] ✅ Health endpoint returns healthy status
- [ ] ✅ API documentation accessible
- [ ] ✅ Vector database statistics retrieved
- [ ] ✅ Empty search returns correct response
- [ ] ✅ Product scraping completed successfully
- [ ] ✅ Products retrieved from database
- [ ] ✅ Enhanced search with results works
- [ ] ✅ Error handling works correctly
- [ ] ✅ Post-application tests pass
- [ ] ✅ Application logs monitored
- [ ] ✅ Clean shutdown completed

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key | ✅ | - |
| `OPENAI_MODEL` | OpenAI model to use | ❌ | `gpt-3.5-turbo` |
| `GCP_PROJECT_ID` | Google Cloud project ID | ✅ | - |
| `GCP_BUCKET_NAME` | Google Cloud Storage bucket | ✅ | - |
| `GCP_CREDENTIALS_PATH` | Path to GCP credentials file | ✅ | - |
| `DB_HOST` | Database host | ❌ | `localhost` |
| `DB_PORT` | Database port | ❌ | `5432` |
| `DB_USER` | Database user | ❌ | `review_user` |
| `DB_PASSWORD` | Database password | ❌ | `review_password` |
| `DB_NAME` | Database name | ❌ | `review_analyzer` |
| `FAISS_INDEX_PATH` | Vector database path | ❌ | `./data/faiss_index` |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health/` | GET | Health check |
| `/docs` | GET | API documentation |
| `/api/v1/products/scrape` | POST | Scrape product reviews |
| `/api/v1/products/{id}` | GET | Get product details |
| `/api/v1/search/reviews` | POST | Search reviews semantically |
| `/api/v1/search/stats` | GET | Vector database statistics |

## 🧪 Testing

### Test Structure

The project uses a multi-layered testing approach:

#### **1. Unit Tests** (`tests/unit/`)
- **Purpose**: Test individual functions and classes in isolation
- **External Dependencies**: None (fully mocked)
- **CI/CD**: Runs on every push/PR
- **Coverage**: Core business logic

#### **2. Mock Tests** (`tests/api/`)
- **Purpose**: Test API endpoints with mocked external services
- **External Dependencies**: Mocked (OpenAI, GCS, VistaPrint)
- **CI/CD**: Runs on every push/PR
- **Coverage**: API functionality and error handling

#### **3. Integration Tests** (`tests/integration/`)
- **Purpose**: Test with real external services
- **External Dependencies**: Real (OpenAI, GCS, VistaPrint)
- **CI/CD**: Runs weekly and on manual trigger
- **Coverage**: End-to-end functionality

### Running Tests Locally

```bash
# Run all tests (unit + mock)
poetry run pytest

# Run specific test categories
poetry run pytest tests/unit/          # Unit tests only
poetry run pytest tests/api/           # API tests with mocks
poetry run pytest tests/integration/   # Integration tests (requires real services)

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_api.py
```

### CI/CD Pipeline

The GitHub Actions pipeline is structured to ensure fast feedback:

#### **Main Pipeline** (runs on every push/PR):
1. **Linting**: Black, Ruff, MyPy
2. **Unit Tests**: Core logic without external dependencies
3. **Mock Tests**: API tests with mocked services
4. **Docker Build**: Verify container builds successfully
5. **Security Scan**: Bandit security analysis

#### **Integration Pipeline** (runs weekly + manual):
1. **Integration Tests**: Tests with real external services
2. **End-to-End Tests**: Full application testing in Docker

**Note**: Integration tests require GitHub secrets to be configured. See [GitHub Secrets Setup](#github-secrets-setup) below.

### Test Configuration

Tests use different configurations based on the environment:

- **Unit/Mock Tests**: `TESTING=true` (uses SQLite in-memory database)
- **Integration Tests**: `TESTING=false` (uses real PostgreSQL and external services)

### Test Types

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test service interactions
- **API Tests**: Test HTTP endpoints with mocked dependencies
- **Mock Tests**: Test with mocked external services

### GitHub Secrets Setup

Integration tests require the following GitHub secrets to be configured in your repository:

1. **GCP_CREDENTIALS_JSON**: Google Cloud Service Account credentials (JSON content)
2. **OPENAI_API_KEY**: OpenAI API key for sentiment analysis
3. **GCP_PROJECT_ID**: Google Cloud Project ID
4. **GCP_BUCKET_NAME**: Google Cloud Storage bucket name

**How to add secrets:**
1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret with the exact name and value

**Note**: The `GCP_CREDENTIALS_JSON` should contain the entire JSON content from your `credentials/gcp-credentials.json` file.

## 🚀 Production Deployment

### Using Docker Compose

```bash
# Build and start
docker-compose up -d --build

# Scale if needed
docker-compose up -d --scale app=3
```

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml review-analyzer
```

### Using Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Error**:
   ```bash
   # Check if PostgreSQL container is running
   docker-compose ps postgres
   
   # Check database logs
   docker-compose logs postgres
   
   # Restart database
   docker-compose restart postgres
   ```

2. **Google Cloud Storage Error**:
   - Verify credentials file path in `.env`
   - Check GCS bucket permissions
   - Ensure GCS API is enabled

3. **OpenAI API Error**:
   - Verify API key is correct
   - Check API key has sufficient credits
   - Ensure you're using a valid model name

4. **Vector Database Issues**:
   - Check if FAISS index files exist in `./data/`
   - Ensure sufficient disk space

### Logs and Monitoring

```bash
# View application logs
docker-compose logs app

# View database logs
docker-compose logs postgres

# Check health status
curl http://localhost:8000/api/v1/health/
```

## 📊 Usage Examples

### Scrape Product Reviews

```bash
curl -X POST "http://localhost:8000/api/v1/products/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.vistaprint.com/promotional-products/drinkware/sports-water-bottles/yeti-r-rambler-r-water-bottle-18-oz",
    "mode": "scrape",
    "force_refresh": false
  }'
```

### Get Product Details

```bash
curl "http://localhost:8000/api/v1/products/{product_id}"
```

### Semantic Search

```bash
curl -X POST "http://localhost:8000/api/v1/search/reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "excellent quality",
    "k": 10
  }'
```

### Health Check

```bash
curl http://localhost:8000/api/v1/health/
```

## 🔒 Security Notes

- ✅ **Never commit credentials** to version control
- ✅ **Use environment variables** for sensitive data
- ✅ **Each user configures their own services** - no shared data access
- ✅ **Isolated data storage** - each user has their own GCS bucket and database
- ✅ **Keep credentials secure** and never share them

## 📋 Detailed Setup Instructions

### Getting OpenAI API Key

1. **Create OpenAI Account**:
   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Sign up or log in
   - Add payment method (required for API access)

2. **Get API Key**:
   - Go to API Keys section
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)

3. **Add Credits**:
   - Go to Billing section
   - Add credits to your account
   - Minimum $5 recommended for testing

### Getting Google Cloud Credentials

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Click "Select a project" → "New Project"
   - Enter project name (e.g., "product-review-analyzer")
   - Click "Create"

2. **Enable APIs**:
   - Go to APIs & Services → Library
   - Search for "Cloud Storage"
   - Click "Cloud Storage" → "Enable"

3. **Create Service Account**:
   - Go to IAM & Admin → Service Accounts
   - Click "Create Service Account"
   - Name: "product-review-analyzer"
   - Description: "Service account for product review analyzer"
   - Click "Create and Continue"

4. **Assign Roles**:
   - Click "Select a role"
   - Search for "Storage Object Admin"
   - Select "Storage Object Admin"
   - Click "Continue" → "Done"

5. **Create Key**:
   - Click on your service account
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose "JSON" format
   - Click "Create"
   - File will download automatically

6. **Setup Credentials**:
   - Rename downloaded file to `gcp-credentials.json`
   - Place it in `credentials/` folder
   - Update `.env` file with your project ID and bucket name

### Creating Google Cloud Storage Bucket

1. **Create Bucket**:
   - Go to Cloud Storage → Buckets
   - Click "Create Bucket"
   - Name: `your-project-name-data-bucket`
   - Location: Choose closest to you
   - Click "Create"

2. **Configure Public Access** (for images):
   - Click on your bucket
   - Go to "Permissions" tab
   - Click "Add" → "New principals"
   - Principal: `allUsers`
   - Role: "Storage Object Viewer"
   - Click "Save"

## 📊 VistaPrint Integration

The system includes a specialized VistaPrint scraper that:

- **Supports multiple modes**: `scrape`, `mock`, `random`
- **Handles pagination**: Automatically fetches all review pages
- **Extracts rich data**: Reviews, ratings, images, verified purchases
- **Robust error handling**: Retries, fallbacks, and comprehensive logging
- **Rate limiting**: Respectful scraping with delays between requests

### Scraping Modes

- **`scrape`**: Scrape from specific URL
- **`mock`**: Use predefined product URLs for testing
- **`random`**: Search and select random product

### Data Structure

```python
VistaPrintProduct:
  - product_id: str
  - name: str
  - url: str
  - reviews: List[VistaPrintReview]

VistaPrintReview:
  - external_id: str
  - title: str
  - description: str
  - rating: int
  - author: str
  - date_posted: datetime
  - is_verified_purchase: bool
  - images: List[str]
```

## 🔄 Database Migrations

### Create migration

```bash
poetry run alembic revision --autogenerate -m "Description"
```

### Apply migrations

```bash
poetry run alembic upgrade head
```

## 🧪 Testing

The project includes a comprehensive testing system with different modes for different environments:

### Test Categories

- **Unit Tests** (`tests/unit/`): Fast, isolated tests that work everywhere
- **Mock Tests** (`tests/api/`): Tests with mocked dependencies that work everywhere
- **Integration Tests** (`tests/integration/`): Tests that require real external services (GCS, OpenAI, etc.)

### Test Modes

The project supports different test modes for different environments:

- **Unit Mode**: Only unit tests (fastest, works everywhere)
- **Mock Mode**: Unit + mock tests (works everywhere)
- **Local Mode**: Unit + mock + local-specific tests
- **Container Mode**: Unit + mock + container-specific tests
- **All Mode**: All tests including integration tests (requires real services)
- **CI Mode**: Unit + mock tests for CI/CD pipeline

### Running Tests

#### Using the Test Runner Script

```bash
# Run tests based on environment (recommended)
python scripts/run_tests.py

# Run specific test modes
python scripts/run_tests.py unit        # Unit tests only
python scripts/run_tests.py mock        # Unit + mock tests
python scripts/run_tests.py local       # Local environment tests
python scripts/run_tests.py container   # Container environment tests
python scripts/run_tests.py all         # All tests (including integration)
python scripts/run_tests.py ci          # CI/CD pipeline tests
```

#### Using Make Commands

```bash
# Run tests based on environment
make test

# Run specific test modes
make test-unit        # Unit tests only
make test-mock        # Unit + mock tests
make test-local       # Local environment tests
make test-container   # Container environment tests
make test-all         # All tests (including integration)
make test-ci          # CI/CD pipeline tests
```

#### Using Poetry Directly

```bash
# Run all tests
poetry run pytest tests/ -v

# Run specific test categories
poetry run pytest tests/unit/ -v                    # Unit tests only
poetry run pytest tests/api/ -v                     # API tests only
poetry run pytest tests/integration/ -v             # Integration tests only

# Run tests with coverage
poetry run pytest tests/ --cov=app --cov-report=html

# Run tests with specific markers
poetry run pytest tests/ -m "unit"                  # Unit tests
poetry run pytest tests/ -m "mock"                  # Mock tests
poetry run pytest tests/ -m "integration"           # Integration tests
poetry run pytest tests/ -m "not integration"       # All tests except integration
```

### Test Environment Variables

The test runner automatically detects the environment:

- `DOCKER_CONTAINER=1`: Runs container mode tests
- `CI=1`: Runs CI mode tests
- Default: Runs local mode tests

### Test Results

- **Unit Tests**: 9/9 passed ✅
- **Mock Tests**: 26/26 passed ✅
- **Integration Tests**: Require real services (run separately)

## 📈 Monitoring

- **Health checks**: `/api/v1/health/`, `/api/v1/health/ready`, `/api/v1/health/live`
- **Logging**: Structured logging with rotation
- **Metrics**: Processing time, success rates, error tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions, please open an issue in the repository.
