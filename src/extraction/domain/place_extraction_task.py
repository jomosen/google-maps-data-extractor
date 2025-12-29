from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .enums.task_status import TaskStatus as Status
from .value_objects.geoname import Geoname


@dataclass
class PlaceExtractionTask:
    """
    Represents a single unit of work within an ExtractionJob.
    Each task defines a search operation starting from a geographic point.
    """

    id: str
    campaign_id: str
    search_seed: str
    geoname: Geoname

    status: Status = Status.PENDING
    attempts: int = 0
    last_error: Optional[str] = None

    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def title(self) -> str:
        return f"{self.search_seed} {self.geoname.name}"

    @staticmethod
    def create(
        campaign_id: str,
        search_seed: str,
        geoname: Geoname,
    ) -> PlaceExtractionTask:
        """Factory method to create a new pending task."""
        return PlaceExtractionTask(
            id=str(uuid.uuid4()),
            campaign_id=campaign_id,
            search_seed=search_seed,
            geoname=geoname,
        )
    
    def mark_running(self) -> None:
        self.status = Status.RUNNING
        self.started_at = datetime.utcnow()
        self.touch()

    def mark_completed(self) -> None:
        self.status = Status.COMPLETED
        self.completed_at = datetime.utcnow()
        self.touch()

    def mark_failed(self, error_message: Optional[str] = None) -> None:
        self.status = Status.FAILED
        self.attempts += 1
        self.last_error = error_message
        self.completed_at = datetime.utcnow()
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
        self.updated_at = datetime.utcnow()
