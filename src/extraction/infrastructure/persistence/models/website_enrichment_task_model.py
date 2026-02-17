from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class WebsitePlaceEnrichmentTaskModel(Base):
    """
    ORM model for WebsitePlaceEnrichmentTask entity.

    This is an independent entity (not part of an aggregate).
    Each task enriches an ExtractedPlace by crawling its website.

    Note: We don't use a foreign key to extracted_places because:
    1. The place might not exist yet when the task is created
    2. Enrichment tasks have their own lifecycle
    3. This follows the eventual consistency pattern
    """

    __tablename__ = "website_enrichment_tasks"

    # Primary key (ULID: 26 characters)
    id: Mapped[str] = mapped_column(String(26), primary_key=True)

    # Reference to the place being enriched (Google Place ID)
    place_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Target URL for website extraction
    website_url: Mapped[str] = mapped_column(Text, nullable=False)

    # Task state
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<WebsitePlaceEnrichmentTaskModel(id={self.id}, place_id={self.place_id}, status={self.status})>"
