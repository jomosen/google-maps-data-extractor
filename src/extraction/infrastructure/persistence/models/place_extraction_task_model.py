from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .campaign_model import CampaignModel


class PlaceExtractionTaskModel(Base):
    """
    ORM model for PlaceExtractionTask entity.

    This is a child entity of Campaign aggregate. Each task represents
    a single search operation for a specific seed + geoname combination.

    The geoname field stores the Geoname value object as JSON.
    """

    __tablename__ = "place_extraction_tasks"

    # Primary key (ULID: 26 characters)
    id: Mapped[str] = mapped_column(String(26), primary_key=True)

    # Foreign key to Campaign
    campaign_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Search parameters
    search_seed: Mapped[str] = mapped_column(String(255), nullable=False)

    # Geoname stored as JSON (Geoname value object)
    geoname: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

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

    # Relationships
    campaign: Mapped["CampaignModel"] = relationship(
        "CampaignModel",
        back_populates="tasks",
    )

    def __repr__(self) -> str:
        return f"<PlaceExtractionTaskModel(id={self.id}, seed={self.search_seed}, status={self.status})>"
