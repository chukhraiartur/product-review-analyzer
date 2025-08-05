"""Database base configuration."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

# Create base class for models
Base = declarative_base()

# Lazy engine and session creation
_engine = None
_SessionLocal = None


def get_engine():
    """Get database engine (lazy initialization)."""
    global _engine
    if _engine is None:
        settings = get_settings()
        if not settings.testing:
            _engine = create_engine(settings.database_url_computed)
        else:
            # Use SQLite for tests
            _engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
            )
    return _engine


def get_session_local():
    """Get session local (lazy initialization)."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


# Database dependency
def get_db():
    """Get database session."""
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()


# Create all tables
def create_tables() -> None:
    """Create all database tables."""
    settings = get_settings()
    # Skip database operations in test environment
    if settings.testing:
        return
    
    Base.metadata.create_all(bind=get_engine())
