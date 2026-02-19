from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

from ..enums.campaign_status import CampaignStatus as CampaignStatus
from ..value_objects.campaign import CampaignConfig as Config
from ..value_objects.ids import CampaignId
from ..exceptions import CampaignError
from .place_extraction_task import PlaceExtractionTask


@dataclass
class Campaign:
    id: CampaignId
    title: str
    status: CampaignStatus
    config: Config

    # Aggregate children
    tasks: List[PlaceExtractionTask] = field(default_factory=list)

    # Counters (managed by App Service or Worker)
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def progress(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return self.completed_tasks / self.total_tasks

    # ---------------------------------------------------------
    # FACTORY
    # ---------------------------------------------------------
    @staticmethod
    def create(title: str | None, config: Config) -> Campaign:
        if not title:
            seed = config.search_seeds[0].title() if config.search_seeds else "Campaign"
            scope_name = config.geoname_selection_params.scope_geoname_name or ""
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            title = f"{seed} {scope_name} {timestamp}".strip()

        return Campaign(
            id=CampaignId.new(),
            title=title,
            status=CampaignStatus.PENDING,
            config=config,
        )

    # ---------------------------------------------------------
    # TASK MANIPULATION (domain-level)
    # ---------------------------------------------------------
    def add_tasks(self, tasks: List[PlaceExtractionTask]) -> None:
        """
        Adds generated tasks to the campaign.
        
        Domain rules:
        - Can only add tasks to PENDING campaigns
        - Cannot add empty task list
        - Cannot add duplicate tasks
        
        Raises:
            CampaignError: If domain rules are violated
        """
        if self.status != CampaignStatus.PENDING:
            raise CampaignError(
                f"Cannot add tasks to {self.status.value} campaign. "
                "Tasks can only be added to PENDING campaigns."
            )
        
        if not tasks:
            raise CampaignError("Cannot add empty task list")
        
        # Validate no duplicates
        existing_ids = {t.id for t in self.tasks}
        duplicate_tasks = [t for t in tasks if t.id in existing_ids]
        if duplicate_tasks:
            duplicate_ids = [str(t.id) for t in duplicate_tasks]
            raise CampaignError(
                f"Duplicate tasks detected: {', '.join(duplicate_ids[:3])}..."
            )
        
        self.tasks.extend(tasks)
        self.total_tasks = len(self.tasks)
        self.touch()

    def mark_task_completed(self) -> None:
        """Increment completed task counter."""
        self.completed_tasks += 1
        self.touch()

    def mark_task_failed(self) -> None:
        """Increment failed task counter."""
        self.failed_tasks += 1
        self.touch()

    # ---------------------------------------------------------
    # STATUS TRANSITIONS
    # ---------------------------------------------------------
    def mark_in_progress(self) -> None:
        """
        Start campaign execution.
        
        Raises:
            CampaignError: If campaign is already finished
        """
        if self.status == CampaignStatus.COMPLETED:
            raise CampaignError("Cannot start a completed campaign")
        if self.status == CampaignStatus.FAILED:
            raise CampaignError("Cannot start a failed campaign")

        self.status = CampaignStatus.IN_PROGRESS
        self.started_at = datetime.now(timezone.utc)
        self.touch()

    def mark_completed(self) -> None:
        """
        Mark campaign as completed.
        
        Raises:
            CampaignError: If campaign is not in progress
        """
        if self.status != CampaignStatus.IN_PROGRESS:
            raise CampaignError(
                f"Cannot complete campaign in {self.status.value} state. "
                "Must be IN_PROGRESS."
            )

        self.status = CampaignStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.touch()

    def mark_failed(self) -> None:
        """
        Mark campaign as failed.

        Raises:
            CampaignError: If campaign is already completed
        """
        if self.status == CampaignStatus.COMPLETED:
            raise CampaignError("Cannot fail a completed campaign")

        self.status = CampaignStatus.FAILED
        self.completed_at = datetime.now(timezone.utc)
        self.touch()

    def resume(self) -> None:
        """
        Resume a failed campaign by resetting it to PENDING.

        Raises:
            CampaignError: If campaign is not in FAILED state
        """
        if self.status != CampaignStatus.FAILED:
            raise CampaignError(
                f"Cannot resume campaign in {self.status.value} state. "
                "Only FAILED campaigns can be resumed."
            )
        self.status = CampaignStatus.PENDING
        self.failed_tasks = 0
        self.completed_at = None
        self.touch()

    def mark_archived(self) -> None:
        """
        Archive a finished campaign (soft removal from active list).

        Raises:
            CampaignError: If campaign is not COMPLETED or FAILED
        """
        if self.status not in {CampaignStatus.COMPLETED, CampaignStatus.FAILED}:
            raise CampaignError(
                f"Cannot archive campaign in {self.status.value} state. "
                "Only COMPLETED or FAILED campaigns can be archived."
            )
        self.status = CampaignStatus.ARCHIVED
        self.touch()

    # ---------------------------------------------------------
    # BUSINESS RULES (Query Methods)
    # ---------------------------------------------------------
    def can_be_started(self) -> bool:
        """
        Check if campaign can be started.
        
        Business rule: Campaign must be PENDING and have at least one task.
        
        Returns:
            True if campaign can transition to IN_PROGRESS
        """
        return self.status == CampaignStatus.PENDING and self.total_tasks > 0

    def can_be_deleted(self) -> bool:
        """
        Check if campaign can be safely deleted.
        
        Business rule: Only PENDING campaigns without tasks can be deleted.
        
        Returns:
            True if campaign can be deleted
        """
        return self.status == CampaignStatus.PENDING and len(self.tasks) == 0

    def has_failed_tasks(self) -> bool:
        """Check if campaign has any failed tasks."""
        return self.failed_tasks > 0

    def completion_percentage(self) -> float:
        """Get completion progress as percentage (0-100)."""
        return self.progress * 100

    # ---------------------------------------------------------
    # INFO
    # ---------------------------------------------------------
    def is_completed(self) -> bool:
        """Check if campaign has completed successfully."""
        return self.status == CampaignStatus.COMPLETED

    def is_finished(self) -> bool:
        """Check if campaign has finished (completed, failed, or archived)."""
        return self.status in {
            CampaignStatus.COMPLETED,
            CampaignStatus.FAILED,
            CampaignStatus.ARCHIVED,
        }

    def can_be_archived(self) -> bool:
        """Check if campaign can be archived."""
        return self.status in {CampaignStatus.COMPLETED, CampaignStatus.FAILED}

    # ---------------------------------------------------------
    # UTIL
    # ---------------------------------------------------------
    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
