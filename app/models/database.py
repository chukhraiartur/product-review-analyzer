"""Database models - backward compatibility module."""

# Import from new structure for backward compatibility
from app.models.database.base import Base, SessionLocal, create_tables, engine, get_db
from app.models.database.product import Product
from app.models.database.review import Review
from app.models.database.review_image import ReviewImage

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "create_tables",
    "Product",
    "Review",
    "ReviewImage",
]
