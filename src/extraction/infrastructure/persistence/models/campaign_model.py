from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .place_extraction_task_model import PlaceExtractionTaskModel


class CampaignModel(Base):
    """
    ORM model for the Campaign aggregate root.

    The config field stores CampaignConfig as JSON since it contains
    nested value objects (geoname_selection_params, enrichment_pools)
    that are typically read/written as a unit.
    """

    __tablename__ = "campaigns"

    # Primary key (ULID: 26 characters)
    id: Mapped[str] = mapped_column(String(26), primary_key=True)

    # Core fields
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # Config stored as JSON (CampaignConfig value object)
    config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Task counters (for efficient querying without loading tasks)
    total_tasks: Mapped[int] = mapped_column(Integer, default=0)
    completed_tasks: Mapped[int] = mapped_column(Integer, default=0)
    failed_tasks: Mapped[int] = mapped_column(Integer, default=0)

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
    tasks: Mapped[list["PlaceExtractionTaskModel"]] = relationship(
        "PlaceExtractionTaskModel",
        back_populates="campaign",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<CampaignModel(id={self.id}, title={self.title}, status={self.status})>"
