.PHONY: help test test-unit test-mock test-local test-container test-all test-ci lint format type-check clean

# Default target
help:
	@echo "Available commands:"
	@echo "  test-unit     - Run unit tests only (work everywhere)"
	@echo "  test-mock     - Run unit + mock tests (work everywhere)"
	@echo "  test-local    - Run tests for local environment"
	@echo "  test-container- Run tests for container environment"
	@echo "  test-all      - Run all tests (including integration)"
	@echo "  test-ci       - Run tests for CI/CD pipeline"
	@echo "  test          - Run tests based on environment (default)"
	@echo "  lint          - Run linting (black + ruff)"
	@echo "  format        - Format code with black"
	@echo "  type-check    - Run type checking with mypy"
	@echo "  clean         - Clean up generated files"

# Test commands
test:
	@python scripts/run_tests.py

test-unit:
	@python scripts/run_tests.py unit

test-mock:
	@python scripts/run_tests.py mock

test-local:
	@python scripts/run_tests.py local

test-container:
	@DOCKER_CONTAINER=1 python scripts/run_tests.py container

test-all:
	@python scripts/run_tests.py all

test-ci:
	@CI=1 python scripts/run_tests.py ci

# Code quality commands
lint:
	@echo "Running Black..."
	@poetry run black --check .
	@echo "Running Ruff..."
	@poetry run ruff check .

format:
	@echo "Formatting code with Black..."
	@poetry run black .
	@echo "Running Ruff auto-fix..."
	@poetry run ruff check . --fix

type-check:
	@echo "Running type checking with MyPy..."
	@poetry run mypy app/

# Docker commands
docker-build:
	@echo "Building Docker image..."
	@docker-compose build

docker-up:
	@echo "Starting Docker containers..."
	@docker-compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	@docker-compose down

docker-test:
	@echo "Running tests in Docker container..."
	@docker-compose exec app python scripts/run_tests.py container

# Cleanup
clean:
	@echo "Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name "htmlcov" -exec rm -rf {} +
	@find . -type f -name "coverage.xml" -delete
	@find . -type f -name ".coverage" -delete 