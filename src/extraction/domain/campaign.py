from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from .enums.campaign_status import CampaignStatus as CampaignStatus
from .value_objects.campaign_config import CampaignConfig as Config
from .place_extraction_task import PlaceExtractionTask as TaskStatus


@dataclass
class Campaign:
    id: str
    title: str
    status: CampaignStatus
    config: Config

    # Aggregate children
    tasks: List[TaskStatus] = field(default_factory=list)

    # Counters (managed by App Service or Worker)
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0

    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def progress(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return self.completed_tasks / self.total_tasks

    # ---------------------------------------------------------
    # FACTORY
    # ---------------------------------------------------------
    @staticmethod
    def create(title: str, config: Config) -> Campaign:
        return Campaign(
            id=str(uuid.uuid4()),
            title=title,
            status=CampaignStatus.PENDING,
            config=config,
        )

    # ---------------------------------------------------------
    # TASK MANIPULATION (domain-level)
    # ---------------------------------------------------------
    def add_tasks(self, tasks: List[TaskStatus]) -> None:
        """Adds generated tasks to the Job.
        Called by the Application Service right before saving the aggregate."""
        self.tasks.extend(tasks)
        self.total_tasks = len(self.tasks)
        self.touch()

    def mark_task_completed(self) -> None:
        self.completed_tasks += 1
        self.touch()

    def mark_task_failed(self) -> None:
        self.failed_tasks += 1
        self.touch()

    # ---------------------------------------------------------
    # STATUS TRANSITIONS
    # ---------------------------------------------------------
    def mark_in_progress(self) -> None:
        if self.status == CampaignStatus.COMPLETED:
            raise ValueError("Cannot start a completed job.")
        if self.status == CampaignStatus.FAILED:
            raise ValueError("Cannot start a failed job.")

        self.status = CampaignStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()
        self.touch()

    def mark_completed(self) -> None:
        if self.status != CampaignStatus.IN_PROGRESS:
            raise ValueError("Cannot complete a job not in progress.")

        self.status = CampaignStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.touch()

    def mark_failed(self) -> None:
        if self.status == CampaignStatus.COMPLETED:
            raise ValueError("Cannot fail a completed job.")

        self.status = CampaignStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.touch()

    # ---------------------------------------------------------
    # INFO
    # ---------------------------------------------------------
    def is_completed(self) -> bool:
        return self.status == CampaignStatus.COMPLETED

    def is_finished(self) -> bool:
        return self.status in {
            CampaignStatus.COMPLETED,
            CampaignStatus.FAILED,
        }

    # ---------------------------------------------------------
    # UTIL
    # ---------------------------------------------------------
    def touch(self) -> None:
        self.updated_at = datetime.utcnow()
