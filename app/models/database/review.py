"""Review database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .review_image import ReviewImage

if TYPE_CHECKING:
    from .product import Product


class Review(Base):
    """Review model for storing product reviews."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, index=True
    )
    external_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True, unique=True
    )
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date_posted: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_verified_purchase: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    sentiment: Mapped[str] = mapped_column(
        String(50), nullable=False, default="neutral"
    )
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="reviews")
    images: Mapped[list["ReviewImage"]] = relationship(
        "ReviewImage", back_populates="review", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Review(id={self.id}, product_id='{self.product_id}', sentiment='{self.sentiment}')>"
