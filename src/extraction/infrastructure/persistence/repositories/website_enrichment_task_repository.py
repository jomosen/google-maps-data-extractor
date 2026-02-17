from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ....domain.entities.place_website_enrichment_task import WebsitePlaceEnrichmentTask
from ....domain.enums.task_status import TaskStatus
from ....domain.interfaces.website_place_enrichment_task_repository import (
    WebsitePlaceEnrichmentTaskRepository,
)
from ....domain.value_objects.ids import EnrichmentTaskId
from ..models import WebsitePlaceEnrichmentTaskModel
from .mappers import enrichment_task_to_model, model_to_enrichment_task


class SqlAlchemyWebsitePlaceEnrichmentTaskRepository(
    WebsitePlaceEnrichmentTaskRepository
):
    """
    SQLAlchemy implementation of WebsitePlaceEnrichmentTaskRepository.

    Handles persistence and atomic claiming of website enrichment tasks.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, task: WebsitePlaceEnrichmentTask) -> None:
        """Persiste la tarea de enriquecimiento (insert o update)."""
        existing = self._session.get(WebsitePlaceEnrichmentTaskModel, task.id.value)

        if existing is None:
            model = enrichment_task_to_model(task)
            self._session.add(model)
        else:
            existing.status = task.status.value
            existing.attempts = task.attempts
            existing.last_error = task.last_error
            existing.started_at = task.started_at
            existing.completed_at = task.completed_at
            existing.updated_at = task.updated_at

    def find_by_id(
        self, task_id: EnrichmentTaskId
    ) -> Optional[WebsitePlaceEnrichmentTask]:
        """Carga la tarea para modificacion."""
        model = self._session.get(WebsitePlaceEnrichmentTaskModel, task_id.value)
        if model is None:
            return None
        return model_to_enrichment_task(model)

    def claim_next_pending(
        self,
        max_attempts: int,
    ) -> Optional[WebsitePlaceEnrichmentTask]:
        """
        Claim the next pending enrichment task for processing.

        Unlike PlaceExtractionTaskRepository, does not require campaign_id
        because enrichment tasks are global.

        Transitions the task from PENDING/FAILED -> IN_PROGRESS.

        Note: For SQLite desktop apps, use TaskDispatcher for multi-worker
        scenarios instead of calling this method directly from workers.
        """
        # Build query for claimable tasks:
        # - PENDING tasks, OR
        # - FAILED tasks with attempts < max_attempts (retryable)
        stmt = (
            select(WebsitePlaceEnrichmentTaskModel)
            .where(
                or_(
                    WebsitePlaceEnrichmentTaskModel.status == TaskStatus.PENDING.value,
                    (
                        (
                            WebsitePlaceEnrichmentTaskModel.status
                            == TaskStatus.FAILED.value
                        )
                        & (WebsitePlaceEnrichmentTaskModel.attempts < max_attempts)
                    ),
                )
            )
            .order_by(WebsitePlaceEnrichmentTaskModel.created_at)
            .limit(1)
        )

        result = self._session.execute(stmt).scalar_one_or_none()

        if result is None:
            return None

        # Transition to IN_PROGRESS
        result.status = TaskStatus.IN_PROGRESS.value
        result.started_at = datetime.now(timezone.utc)
        result.updated_at = datetime.now(timezone.utc)

        return model_to_enrichment_task(result)

    def find_pending_ids(
        self,
        max_attempts: int,
    ) -> list[EnrichmentTaskId]:
        """
        Get all pending enrichment task IDs.

        Used by TaskDispatcher to load tasks into the queue.
        Includes FAILED tasks that haven't exceeded max_attempts.
        """
        stmt = (
            select(WebsitePlaceEnrichmentTaskModel.id)
            .where(
                or_(
                    WebsitePlaceEnrichmentTaskModel.status == TaskStatus.PENDING.value,
                    (
                        (
                            WebsitePlaceEnrichmentTaskModel.status
                            == TaskStatus.FAILED.value
                        )
                        & (WebsitePlaceEnrichmentTaskModel.attempts < max_attempts)
                    ),
                )
            )
            .order_by(WebsitePlaceEnrichmentTaskModel.created_at)
        )

        results = self._session.execute(stmt).scalars().all()
        return [EnrichmentTaskId(task_id) for task_id in results]
