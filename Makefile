.PHONY: help install dev test lint format type-check init-db start clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	poetry install

dev: ## Start development server
	poetry run dev

start: ## Start production server
	poetry run start

test: ## Run all tests
	poetry run pytest tests/ -v

test-unit: ## Run unit tests only (fast, no external dependencies)
	poetry run pytest tests/unit/ -v -m "unit"

test-api: ## Run API tests only (with mocks)
	poetry run pytest tests/api/ -v -m "api"

test-integration: ## Run integration tests only (require external services)
	poetry run pytest tests/integration/ -v -m "integration"

test-gcs: ## Run GCS tests only
	poetry run pytest tests/ -v -m "gcs"

test-mock: ## Run tests with mocks only
	poetry run pytest tests/ -v -m "mock"

test-fast: ## Run fast tests (unit + api with mocks)
	poetry run pytest tests/unit/ tests/api/ -v -m "unit or api"

test-cov: ## Run tests with coverage
	poetry run pytest tests/ -v --cov=app --cov-report=html:htmlcov --cov-report=term-missing

lint: ## Run linter
	poetry run lint

format: ## Format code
	poetry run format

type-check: ## Run type checker
	poetry run type-check

init-db: ## Initialize database
	poetry run init-db

migrate: ## Run database migrations
	poetry run alembic upgrade head

migrate-create: ## Create new migration
	poetry run alembic revision --autogenerate -m "$(message)"

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf coverage.xml 