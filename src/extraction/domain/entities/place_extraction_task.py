from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, ClassVar

from ..enums.task_status import TaskStatus as Status
from ..value_objects.geo import Geoname
from ..value_objects.ids import CampaignId, ExtractionTaskId
from ..events import TaskStartedEvent, TaskCompletedEvent, TaskFailedEvent
from ..exceptions import TaskError
from shared.events import EventBus


@dataclass
class PlaceExtractionTask:
    """
    Represents a single unit of work within a Campaign.
    Each task defines a search operation starting from a geographic point.
    
    Domain Constants:
    - MAX_ATTEMPTS: Maximum retry attempts before task is permanently failed
    
    Domain Events:
    - Emits events on state changes for interested subscribers
    """
    
    # Domain constant (ClassVar = not a dataclass field)
    MAX_ATTEMPTS: ClassVar[int] = 3

    id: ExtractionTaskId
    campaign_id: CampaignId
    search_seed: str
    geoname: Geoname
    event_bus: EventBus  # Added for event publishing

    status: Status = Status.PENDING
    attempts: int = 0
    last_error: Optional[str] = None
    places_extracted: int = 0  # Track progress

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
        event_bus: EventBus,
    ) -> PlaceExtractionTask:
        """Factory method to create a new pending task."""
        return PlaceExtractionTask(
            id=ExtractionTaskId.new(),
            campaign_id=campaign_id,
            search_seed=search_seed,
            geoname=geoname,
            event_bus=event_bus,
        )

    def mark_in_progress(self) -> None:
        self.status = Status.IN_PROGRESS
        self.started_at = datetime.now(timezone.utc)
        self.touch()
        
        # Emit event
        asyncio.create_task(self.event_bus.publish(
            TaskStartedEvent(
                occurred_at=datetime.now(),
                aggregate_id=str(self.id),
                task_id=str(self.id),
                search_seed=self.search_seed,
                location=self.geoname.name
            )
        ))

    def mark_completed(self) -> None:
        self.status = Status.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.touch()
        
        # Emit event
        asyncio.create_task(self.event_bus.publish(
            TaskCompletedEvent(
                occurred_at=datetime.now(),
                aggregate_id=str(self.id),
                task_id=str(self.id),
                total_places_extracted=self.places_extracted,
                duration_seconds=(
                    (self.completed_at - self.started_at).total_seconds()
                    if self.started_at else None
                )
            )
        ))

    def mark_failed(self, error_message: Optional[str] = None) -> None:
        """
        Mark task as failed.
        
        Automatically increments attempt counter.
        
        Args:
            error_message: Optional error description
        """
        self.status = Status.FAILED
        self.attempts += 1
        self.last_error = error_message
        self.completed_at = datetime.now(timezone.utc)
        self.touch()
        
        # Emit event
        asyncio.create_task(self.event_bus.publish(
            TaskFailedEvent(
                occurred_at=datetime.now(),
                aggregate_id=str(self.id),
                task_id=str(self.id),
                error=error_message or "Unknown error",
                places_extracted_before_failure=self.places_extracted
            )
        ))

    def mark_pending(self) -> None:
        """
        Reset task to PENDING status.
        
        Raises:
            TaskError: If task is already completed
        """
        if self.status == Status.COMPLETED:
            raise TaskError("Cannot mark a completed task as pending")
        self.status = Status.PENDING
        self.touch()

    def increment_attempt(self) -> None:
        """
        Increment attempt counter.
        
        Raises:
            TaskError: If max attempts already reached
        """
        if self.attempts >= self.MAX_ATTEMPTS:
            raise TaskError(
                f"Max attempts ({self.MAX_ATTEMPTS}) already reached. "
                "Cannot increment further."
            )
        
        self.attempts += 1
        self.touch()

    # ---------------------------------------------------------
    # BUSINESS RULES (Query Methods)
    # ---------------------------------------------------------
    def can_retry(self) -> bool:
        """
        Check if task can be retried.
        
        Business rule: Task must be FAILED and not have exceeded max attempts.
        
        Returns:
            True if task can be retried
        """
        return self.status == Status.FAILED and self.attempts < self.MAX_ATTEMPTS

    def is_exhausted(self) -> bool:
        """
        Check if task has exhausted all retry attempts.
        
        Returns:
            True if attempts >= MAX_ATTEMPTS
        """
        return self.attempts >= self.MAX_ATTEMPTS

    def is_in_final_state(self) -> bool:
        """
        Check if task is in a final state (cannot transition further).
        
        Returns:
            True if COMPLETED or FAILED with exhausted attempts
        """
        return self.status == Status.COMPLETED or (
            self.status == Status.FAILED and self.is_exhausted()
        )

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
