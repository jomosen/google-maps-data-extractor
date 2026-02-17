from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .enums.task_status import TaskStatus as Status
from .value_objects.geoname import Geoname
from .value_objects.ids import CampaignId, ExtractionTaskId


@dataclass
class PlaceExtractionTask:
    """
    Represents a single unit of work within a Campaign.
    Each task defines a search operation starting from a geographic point.
    """

    id: ExtractionTaskId
    campaign_id: CampaignId
    search_seed: str
    geoname: Geoname

    status: Status = Status.PENDING
    attempts: int = 0
    last_error: Optional[str] = None

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def title(self) -> str:
        return f"{self.search_seed} {self.geoname.name}"

    @staticmethod
    def create(
        campaign_id: CampaignId,
        search_seed: str,
        geoname: Geoname,
    ) -> PlaceExtractionTask:
        """Factory method to create a new pending task."""
        return PlaceExtractionTask(
            id=ExtractionTaskId.new(),
            campaign_id=campaign_id,
            search_seed=search_seed,
            geoname=geoname,
        )

    def mark_in_progress(self) -> None:
        self.status = Status.IN_PROGRESS
        self.started_at = datetime.now(timezone.utc)
        self.touch()

    def mark_completed(self) -> None:
        self.status = Status.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.touch()

    def mark_failed(self, error_message: Optional[str] = None) -> None:
        self.status = Status.FAILED
        self.attempts += 1
        self.last_error = error_message
        self.completed_at = datetime.now(timezone.utc)
        self.touch()

    def mark_pending(self) -> None:
        if self.status == Status.COMPLETED:
            raise ValueError("Cannot mark a completed task as pending.")
        self.status = Status.PENDING
        self.touch()

    def can_retry(self, max_attempts: int) -> bool:
        return (
            self.status == Status.FAILED
            and self.attempts < max_attempts
        )

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
