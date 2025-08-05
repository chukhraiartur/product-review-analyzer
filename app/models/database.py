"""Database models - backward compatibility module."""

# Import from new structure for backward compatibility
from app.models.database.base import (
    Base,
    create_tables,
    get_db,
    get_engine,
    get_session_local,
)
from app.models.database.product import Product
from app.models.database.review import Review
from app.models.database.review_image import ReviewImage

__all__ = [
    "Base",
    "get_engine",
    "get_session_local",
    "get_db",
    "create_tables",
    "Product",
    "Review",
    "ReviewImage",
]
