from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .extracted_place_review_model import ExtractedPlaceReviewModel


class ExtractedPlaceModel(Base):
    """
    ORM model for the ExtractedPlace aggregate root.

    Complex value objects (attributes, hours, booking_options, enrichments)
    are stored as JSON columns.

    The place_id is the external Google Place ID (not a ULID).
    """

    __tablename__ = "extracted_places"

    # Primary key: Google Place ID (external identifier)
    place_id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Reference to the extraction task that created this place
    task_id: Mapped[str | None] = mapped_column(String(26), nullable=True, index=True)

    # Core identification
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cid: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Location
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    plus_code: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Ratings and reviews
    rating: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Contact and links
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    website_link: Mapped[str | None] = mapped_column(Text, nullable=True)
    menu_link: Mapped[str | None] = mapped_column(Text, nullable=True)
    appointment_link: Mapped[str | None] = mapped_column(Text, nullable=True)
    booking_link: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_online_link: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Category and description
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    main_image: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Business status
    closure_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    claimable: Mapped[bool | None] = mapped_column(Boolean, default=False)
    average_price: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Complex nested objects stored as JSON
    attributes: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    hours: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    booking_options: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    review_summary: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    # Enrichment tracking (IntFlag stored as integer)
    enrichment_status: Mapped[int] = mapped_column(Integer, default=0)

    # Polymorphic enrichments stored as JSON array
    enrichments: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    reviews: Mapped[list["ExtractedPlaceReviewModel"]] = relationship(
        "ExtractedPlaceReviewModel",
        back_populates="place",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<ExtractedPlaceModel(place_id={self.place_id}, name={self.name})>"
