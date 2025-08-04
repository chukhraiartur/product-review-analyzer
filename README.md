# Product Review Analyzer

AI-powered product review analysis system with VistaPrint integration, sentiment analysis, and semantic search capabilities.

## 🚀 Features

- **VistaPrint Integration**: Scrape product reviews from VistaPrint with full pagination support
- **AI Sentiment Analysis**: Analyze review sentiment using OpenAI GPT-4
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

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL (or use Docker)
- OpenAI API key
- Google Cloud Storage account and credentials

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

## 🚀 Quick Start

### **For New Users (Each user sets up their own services)**

**Important**: Each user must configure their own services. Data is not shared between users for security and cost control.

## 🐳 **Docker Deployment (Recommended)**

### **Prerequisites**
- Docker and Docker Compose installed
- Git installed
- Internet connection

### **Step 1: Clone and Setup**
```bash
# Clone the repository
git clone https://github.com/your-username/product-review-analyzer.git
cd product-review-analyzer

# Copy environment file
cp env.example .env
```

### **Step 2: Configure Services**

#### **A. OpenAI API Setup**
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create account and add payment method
3. Get API key from API Keys section
4. Add credits (minimum $5 recommended)
5. Update `.env`:
   ```env
   OPENAI_API_KEY=sk-your-api-key-here
   OPENAI_MODEL=gpt-3.5-turbo
   ```

#### **B. Google Cloud Storage Setup**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable Cloud Storage API
4. Create service account with Storage Object Admin role
5. Download JSON credentials file
6. Rename to `gcp-credentials.json` and place in `credentials/` folder
7. Create storage bucket with public access for images
8. Update `.env`:
   ```env
   GCP_PROJECT_ID=your-project-id
   GCP_BUCKET_NAME=your-bucket-name
   GCP_CREDENTIALS_PATH=./credentials/gcp-credentials.json
   ```

### **Step 3: Run with Docker**
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
```

### **Step 4: Verify Installation**
```bash
# Check health endpoint
curl http://localhost:8000/health

# Open API documentation
open http://localhost:8000/docs
```

### **Step 5: Test Scraping**
```bash
# Scrape a product (example URL)
curl -X POST "http://localhost:8000/api/v1/products/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.vistaprint.com/promotional-products/drinkware/sports-water-bottles/yeti-r-rambler-r-water-bottle-18-oz",
    "mode": "scrape",
    "force_refresh": false
  }'
```

### **Step 6: Get Results**
```bash
# Get product details
curl http://localhost:8000/api/v1/products/1

# Search reviews
curl -X POST "http://localhost:8000/api/v1/search/reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "great quality",
    "k": 5
  }'
```

## 💻 **Local Development Setup**

### **Prerequisites**
- Python 3.11+
- Poetry
- PostgreSQL (or use Docker)

### **Step 1: Setup Database**
```bash
# Option A: Use Docker for database only
docker-compose -f docker-compose.dev.yml up -d postgres

# Option B: Install PostgreSQL locally
# Create database and user manually
```

### **Step 2: Install Dependencies**
```bash
# Install Poetry if not installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### **Step 3: Configure Environment**
```bash
# Copy environment file
cp env.example .env

# Edit .env with your settings
# (Follow same steps as Docker setup above)
```

### **Step 4: Initialize Database**
```bash
# Create database tables
poetry run python scripts/init_db.py
```

### **Step 5: Run Application**
```bash
# Start the application
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔧 **Configuration**

### **Environment Variables**

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

### **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/docs` | GET | API documentation |
| `/api/v1/products/scrape` | POST | Scrape product reviews |
| `/api/v1/products/{id}` | GET | Get product details |
| `/api/v1/search/reviews` | POST | Search reviews semantically |

## 🧪 **Testing**

### **Run Tests**
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test file
poetry run pytest tests/test_api.py
```

### **Test Types**
- **Unit Tests**: Test individual functions
- **Integration Tests**: Test service interactions
- **API Tests**: Test HTTP endpoints
- **Mock Tests**: Test with mocked external services

## 🚀 **Production Deployment**

### **Using Docker Compose**
```bash
# Build and start
docker-compose up -d --build

# Scale if needed
docker-compose up -d --scale app=3
```

### **Using Docker Swarm**
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml review-analyzer
```

### **Using Kubernetes**
```bash
# Apply manifests
kubectl apply -f k8s/
```

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Database Connection Failed**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

#### **OpenAI API Errors**
- Verify API key is correct
- Check if you have sufficient credits
- Ensure model name is correct

#### **GCS Connection Issues**
- Verify credentials file exists
- Check bucket permissions
- Ensure project ID is correct

#### **Application Won't Start**
```bash
# Check logs
docker-compose logs app

# Rebuild container
docker-compose up -d --build app
```

### **Logs and Monitoring**
```bash
# View application logs
docker-compose logs -f app

# View database logs
docker-compose logs -f postgres

# Check health status
curl http://localhost:8000/health
```

## 📊 **Usage Examples**

### **Scrape Product Reviews**
```bash
curl -X POST "http://localhost:8000/api/v1/products/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.vistaprint.com/promotional-products/drinkware/sports-water-bottles/yeti-r-rambler-r-water-bottle-18-oz",
    "mode": "scrape",
    "force_refresh": false
  }'
```

### **Get Product Details**
```bash
curl http://localhost:8000/api/v1/products/1
```

### **Search Reviews**
```bash
curl -X POST "http://localhost:8000/api/v1/search/reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "excellent quality",
    "k": 10
  }'
```

### **Health Check**
```bash
curl http://localhost:8000/health
```

## 🔒 **Security Notes**

- ✅ **Never commit credentials** to version control
- ✅ **Use environment variables** for sensitive data
- ✅ **Each user configures their own services** - no shared data access
- ✅ **Isolated data storage** - each user has their own GCS bucket and database
- ✅ **Keep credentials secure** and never share them

### 1. Clone the repository

```bash
git clone <repository-url>
cd product-review-analyzer
```

### 2. Set up environment variables

```bash
cp env.example .env
```

Edit `.env` file with your configuration:

```env
# Database settings
# Note: If you have local PostgreSQL installed, use DB_PORT=5433 to avoid conflicts
DB_HOST=localhost
DB_PORT=5433
DB_USER=review_user
DB_PASSWORD=review_password
DB_NAME=review_analyzer

# OpenAI settings
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Google Cloud Storage settings
GCP_PROJECT_ID=your-gcp-project-id
GCP_BUCKET_NAME=your-gcp-bucket-name
GCP_CREDENTIALS_PATH=./credentials/gcp-credentials.json

# API settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
```

### 3. Install dependencies

```bash
poetry install
```

### 4. Start PostgreSQL with Docker

```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 5. Initialize database

```bash
# Option 1: Using Poetry script
poetry run init-db

# Option 2: Using Makefile
make init-db

# Option 3: Direct script execution
python scripts/init_db.py
```

### 6. Run the application

```bash
# Option 1: Using Poetry script
poetry run dev

# Option 2: Using Makefile
make dev

# Option 3: Direct uvicorn command
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Access the API

- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 🛠️ Development Commands

### Using Poetry Scripts

```bash
# Initialize database
poetry run init-db

# Start development server
poetry run dev

# Run tests
poetry run test

# Run tests with coverage
poetry run test-cov

# Run linter
poetry run lint

# Format code
poetry run format

# Type checking
poetry run type-check
```

### Using Makefile

```bash
# Show all available commands
make help

# Install dependencies
make install

# Start development server
make dev

# Run tests
make test

# Run tests with coverage
make test-cov

# Format and lint code
make format
make lint

# Type checking
make type-check

# Initialize database
make init-db

# Run database migrations
make migrate

# Clean generated files
make clean
```

## 📚 API Endpoints

### Products

- `POST /api/v1/products/scrape` - Scrape product reviews from VistaPrint
- `GET /api/v1/products/{product_id}` - Get product details with reviews
- `GET /api/v1/products/` - List all products

### Search

- `POST /api/v1/search/reviews` - Semantic search in reviews
- `GET /api/v1/search/stats` - Vector database statistics

### Health

- `GET /health` - Application health check
- `GET /health/ready` - Readiness check
- `GET /health/live` - Liveness check

## 🔧 Usage Examples

### Scrape VistaPrint Product

```bash
curl -X POST "http://localhost:8000/api/v1/products/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.vistaprint.com/photo-gifts/paper-coasters",
    "mode": "scrape"
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
    "query": "quality product",
    "limit": 10
  }'
```

## 🧪 Testing

The project includes comprehensive testing with different types of tests:

### Test Types

- **Unit Tests** (`-m "unit"`): Test individual functions and classes in isolation
- **Integration Tests** (`-m "integration"`): Test interactions between components
- **API Tests** (`-m "api"`): Test FastAPI endpoints and HTTP responses
- **GCS Tests** (`-m "gcs"`): Test Google Cloud Storage functionality

### Running Tests

```bash
# Run all tests
poetry run pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test types
poetry run pytest tests/ -m "unit" -v
poetry run pytest tests/ -m "integration" -v
poetry run pytest tests/ -m "api" -v
poetry run pytest tests/ -m "gcs" -v

# Run with Makefile
make test              # All tests
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-api          # API tests only
make test-gcs          # GCS tests only
```

### Test Coverage

- **Minimum Coverage**: 70%
- **Coverage Reports**: HTML and XML formats
- **Coverage Location**: `htmlcov/` directory

### Why Some Tests Are Limited

- **End-to-End Tests**: Not implemented due to external dependencies (VistaPrint, OpenAI)
- **Performance Tests**: Not implemented due to CI/CD time constraints
- **Load Tests**: Not implemented due to infrastructure requirements

### Run linting

```bash
poetry run black app/ tests/
poetry run ruff check app/ tests/
poetry run mypy app/
```

## 🐳 Docker Deployment

### Development

```bash
# Start only PostgreSQL
docker-compose -f docker-compose.dev.yml up -d

# Run application locally
poetry run uvicorn app.main:app --reload
```

### Production

```bash
# Start full stack
docker-compose up -d
```

## ☁️ Google Cloud Storage Integration

The system uses Google Cloud Storage for intelligent file management with the following features:

### ✅ **Completed Integration**

- **HTML Caching**: VistaPrint scraper automatically saves HTML pages to GCS
- **Force Refresh**: API parameter controls whether to use cached HTML or fetch fresh content
- **Structured Storage**: Files organized by date and product slug
- **Error Handling**: Scraping continues even if GCS operations fail
- **Logging**: Comprehensive logging of GCS operations

## 🤖 OpenAI Integration

The system uses OpenAI GPT models for sentiment analysis of product reviews.

### ✅ **Completed Integration**

- **Sentiment Analysis**: Automatic analysis of review sentiment (positive, neutral, negative)
- **Fallback Mechanism**: Keyword-based analysis when OpenAI API is unavailable
- **Batch Processing**: Support for analyzing multiple reviews
- **Confidence Scoring**: Sentiment confidence and reasoning
- **Error Handling**: Graceful degradation when API fails

## 🔍 FAISS Vector Database

The system uses FAISS for semantic search of reviews using vector embeddings.

### ✅ **Completed Integration**

- **Vector Embeddings**: Automatic generation of review embeddings using Sentence Transformers
- **Semantic Search**: Find similar reviews using cosine similarity
- **Local Storage**: FAISS index stored locally for fast access
- **Metadata Storage**: Review IDs and texts stored alongside embeddings
- **Search API**: RESTful endpoints for semantic review search

### Storage Structure

```
bucket-name/
├── html/
│   └── year=YYYY/
│       └── month=MM/
│           └── day=DD/
│               └── product_slug_timestamp.html
├── images/
│   └── product_slug/
│       ├── external_id_1.jpg
│       ├── external_id_2.jpg
│       └── external_id_3.jpg
└── logs/
    └── year=YYYY/
        └── month=MM/
            └── day=DD/
                └── logs_timestamp.txt
```

### Key Features

- **HTML Caching**: 24-hour cache for product HTML pages to reduce scraping overhead
- **Force Refresh**: API parameter to bypass cache and fetch fresh HTML
- **Image Storage**: Automatic download and storage of review images with deduplication
- **Structured Organization**: Date-based folder structure for easy management
- **Public Access**: Images are publicly accessible for web display
- **Automatic Cleanup**: Configurable retention policy for old files

### API Parameters

- **`force_refresh`**: Boolean parameter to force new HTML scraping (default: false)
- **Cache Strategy**: Use existing HTML if available and less than 24 hours old
- **Image Deduplication**: Skip existing images, only download new ones

### Setup Instructions

#### **Option 1: Using Service Account JSON (Recommended)**

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing
   - Enable Cloud Storage API

2. **Create Service Account**:
   - IAM & Admin → Service Accounts
   - Create service account with Storage Object Admin role
   - Download JSON credentials file

3. **Create Storage Bucket**:
   - Cloud Storage → Buckets
   - Create bucket with unique name
   - Configure public access for images

4. **Setup Credentials File**:
   ```bash
   # Place your credentials file in the credentials folder
   # Rename it to gcp-credentials.json
   # The file should be at: credentials/gcp-credentials.json
   ```

5. **Configure Environment**:
   ```env
   GCP_PROJECT_ID=your-project-id
   GCP_BUCKET_NAME=your-bucket-name
   GCP_CREDENTIALS_PATH=./credentials/gcp-credentials.json
   ```

#### **Option 2: Using Default Credentials (Local Development)**

For local development, you can use Google Cloud CLI:

```bash
# Install Google Cloud CLI
gcloud auth application-default login

# Set project
gcloud config set project your-project-id

# No need to set GCP_CREDENTIALS_JSON in .env
```

### 🔒 **Security Notes**

- ✅ **Never commit credentials files** to version control
- ✅ **Use environment variables** for credentials
- ✅ **GitHub Secrets** for CI/CD deployment
- ✅ **Local .env file** for development (already in .gitignore)
- ✅ **Each user configures their own services** - no shared data access
- ✅ **Isolated data storage** - each user has their own GCS bucket and database

## 📋 **Detailed Setup Instructions**

### **Getting OpenAI API Key**

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

### **Getting Google Cloud Credentials**

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

### **Creating Google Cloud Storage Bucket**

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

### **Setting up PostgreSQL Database**

**Option 1: Using Docker (Recommended for testing)**
```bash
# Start PostgreSQL with Docker
docker-compose -f docker-compose.dev.yml up -d

# Database will be available at:
# Host: localhost
# Port: 5433
# User: review_user
# Password: review_password
# Database: review_analyzer
```

**Option 2: Using local PostgreSQL**
```bash
# Install PostgreSQL locally
# Create database and user
# Update .env with your settings
```
   GCP_BUCKET_NAME=your-bucket-name
   GCP_CREDENTIALS_PATH=./credentials/gcp-credentials.json
   ```

5. **Place Credentials**:
   - Create `credentials/` folder
   - Place JSON file as `gcp-credentials.json`

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

## 📈 Monitoring

- **Health checks**: `/health`, `/health/ready`, `/health/live`
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