from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .enums.task_status import TaskStatus as Status


@dataclass
class WebsitePlaceEnrichmentTask:
    """
    Represents a unit of work to enrich an ExtractedPlace using its website.
    Triggered after initial place extraction is completed.
    """

    id: str
    place_id: str  # The reference to the ExtractedPlace being enriched
    website_url: str # The target URL for the WebsiteExtractor
    
    status: Status = Status.PENDING
    attempts: int = 0
    last_error: Optional[str] = None

    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def title(self) -> str:
        return f"Enrichment for Place {self.place_id} via {self.website_url}"

    @staticmethod
    def create(
        place_id: str,
        website_url: str,
    ) -> WebsitePlaceEnrichmentTask:
        """Factory method to create a new pending enrichment task."""
        return WebsitePlaceEnrichmentTask(
            id=str(uuid.uuid4()),
            place_id=place_id,
            website_url=website_url,
        )
    
    def mark_running(self) -> None:
        self.status = Status.RUNNING
        self.started_at = datetime.utcnow()
        self.touch()

    def mark_completed(self) -> None:
        """Called when WebsiteExtractor successfully produces EnrichedPlaceData."""
        self.status = Status.COMPLETED
        self.completed_at = datetime.utcnow()
        self.touch()

    def mark_failed(self, error_message: Optional[str] = None) -> None:
        self.status = Status.FAILED
        self.attempts += 1
        self.last_error = error_message
        self.completed_at = datetime.utcnow()
        self.touch()

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()