from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from ..enums.task_status import TaskStatus as Status
from ..value_objects.ids import EnrichmentTaskId, PlaceId


@dataclass
class WebsitePlaceEnrichmentTask:
    """
    Represents a unit of work to enrich an ExtractedPlace using its website.
    """

    id: EnrichmentTaskId
    place_id: PlaceId  # The reference to the ExtractedPlace being enriched
    website_url: str # The target URL for the WebsiteExtractor

    status: Status = Status.PENDING
    attempts: int = 0
    last_error: Optional[str] = None

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def title(self) -> str:
        return f"Enrichment for Place {self.place_id} via {self.website_url}"

    @staticmethod
    def create(
        place_id: PlaceId,
        website_url: str,
    ) -> WebsitePlaceEnrichmentTask:
        """Factory method to create a new pending enrichment task."""
        return WebsitePlaceEnrichmentTask(
            id=EnrichmentTaskId.new(),
            place_id=place_id,
            website_url=website_url,
        )

    def mark_in_progress(self) -> None:
        self.status = Status.IN_PROGRESS
        self.started_at = datetime.now(timezone.utc)
        self.touch()

    def mark_completed(self) -> None:
        """Called when WebsiteExtractor successfully produces EnrichedPlaceData."""
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

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
