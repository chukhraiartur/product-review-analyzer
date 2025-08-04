#!/usr/bin/env python3
"""Database initialization script."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.models.database import create_tables


def main():
    """Initialize database tables and required directories."""
    # Setup logging
    setup_logging(log_level="INFO")
    logger = get_logger(__name__)

    logger.info("Starting database initialization...")

    try:
        # Create tables
        logger.info("Creating database tables...")
        create_tables()
        logger.info("Database tables created successfully")

        # Create required directories
        directories = ["data", "logs"]
        for dir_name in directories:
            dir_path = Path(dir_name)
            dir_path.mkdir(exist_ok=True)
            logger.info(f"Directory '{dir_name}' ready")

        logger.info("Database initialization completed successfully")
        logger.info(f"Database URL: {settings.database_url_computed}")

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
