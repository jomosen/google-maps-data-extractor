from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ....domain.entities.place_extraction_task import PlaceExtractionTask
from ....domain.enums.task_status import TaskStatus
from ....domain.interfaces.place_extraction_task_repository import (
    PlaceExtractionTaskRepository,
)
from ....domain.value_objects.ids import CampaignId, ExtractionTaskId
from ..models import PlaceExtractionTaskModel
from .mappers import model_to_task, task_to_model


class SqlAlchemyPlaceExtractionTaskRepository(PlaceExtractionTaskRepository):
    """
    SQLAlchemy implementation of PlaceExtractionTaskRepository.

    Handles persistence and atomic claiming of extraction tasks.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, task: PlaceExtractionTask) -> None:
        """Persiste la tarea (insert o update)."""
        existing = self._session.get(PlaceExtractionTaskModel, task.id.value)

        if existing is None:
            model = task_to_model(task)
            self._session.add(model)
        else:
            existing.status = task.status.value
            existing.attempts = task.attempts
            existing.last_error = task.last_error
            existing.started_at = task.started_at
            existing.completed_at = task.completed_at
            existing.updated_at = task.updated_at

    def find_by_id(self, task_id: ExtractionTaskId) -> Optional[PlaceExtractionTask]:
        """Carga la tarea para modificacion."""
        model = self._session.get(PlaceExtractionTaskModel, task_id.value)
        if model is None:
            return None
        return model_to_task(model)

    def claim_next_pending(
        self,
        campaign_id: CampaignId,
        max_attempts: int,
    ) -> Optional[PlaceExtractionTask]:
        """
        Claim the next pending task for processing.

        Transitions the task from PENDING/FAILED -> IN_PROGRESS.

        Note: For SQLite desktop apps, use TaskDispatcher for multi-worker
        scenarios instead of calling this method directly from workers.
        """
        # Build query for claimable tasks:
        # - PENDING tasks, OR
        # - FAILED tasks with attempts < max_attempts (retryable)
        stmt = (
            select(PlaceExtractionTaskModel)
            .where(PlaceExtractionTaskModel.campaign_id == campaign_id.value)
            .where(
                or_(
                    PlaceExtractionTaskModel.status == TaskStatus.PENDING.value,
                    (
                        (PlaceExtractionTaskModel.status == TaskStatus.FAILED.value)
                        & (PlaceExtractionTaskModel.attempts < max_attempts)
                    ),
                )
            )
            .order_by(PlaceExtractionTaskModel.created_at)
            .limit(1)
        )

        result = self._session.execute(stmt).scalar_one_or_none()

        if result is None:
            return None

        # Transition to IN_PROGRESS
        result.status = TaskStatus.IN_PROGRESS.value
        result.started_at = datetime.now(timezone.utc)
        result.updated_at = datetime.now(timezone.utc)

        return model_to_task(result)

    def find_pending_ids(
        self,
        campaign_id: CampaignId,
        max_attempts: int,
    ) -> list[ExtractionTaskId]:
        """
        Get all pending task IDs for a campaign.

        Used by TaskDispatcher to load tasks into the queue.
        Includes FAILED tasks that haven't exceeded max_attempts.
        """
        stmt = (
            select(PlaceExtractionTaskModel.id)
            .where(PlaceExtractionTaskModel.campaign_id == campaign_id.value)
            .where(
                or_(
                    PlaceExtractionTaskModel.status == TaskStatus.PENDING.value,
                    (
                        (PlaceExtractionTaskModel.status == TaskStatus.FAILED.value)
                        & (PlaceExtractionTaskModel.attempts < max_attempts)
                    ),
                )
            )
            .order_by(PlaceExtractionTaskModel.created_at)
        )

        results = self._session.execute(stmt).scalars().all()
        return [ExtractionTaskId(task_id) for task_id in results]
