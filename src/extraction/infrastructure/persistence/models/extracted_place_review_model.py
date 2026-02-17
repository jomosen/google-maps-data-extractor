from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .extracted_place_model import ExtractedPlaceModel


class ExtractedPlaceReviewModel(Base):
    """
    ORM model for ExtractedPlaceReview entity.

    This is a child entity of ExtractedPlace aggregate. Each review
    is associated with a place via place_id foreign key.
    """

    __tablename__ = "extracted_place_reviews"

    # Primary key (ULID: 26 characters)
    id: Mapped[str] = mapped_column(String(26), primary_key=True)

    # Foreign key to ExtractedPlace (Google Place ID)
    place_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("extracted_places.place_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Review content
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    lang: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Photos stored as JSON array
    photos: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # Original review date (from Google)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    place: Mapped["ExtractedPlaceModel"] = relationship(
        "ExtractedPlaceModel",
        back_populates="reviews",
    )

    def __repr__(self) -> str:
        return f"<ExtractedPlaceReviewModel(id={self.id}, author={self.author})>"
