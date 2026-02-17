from __future__ import annotations

import queue
import threading
from typing import Generic, TypeVar

from ...domain.interfaces.unit_of_work import AbstractUnitOfWork
from ...domain.value_objects.ids import CampaignId, EnrichmentTaskId, ExtractionTaskId
from shared.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", ExtractionTaskId, EnrichmentTaskId)


class TaskDispatcher(Generic[T]):
    """
    Thread-safe task dispatcher using an in-memory queue.

    Designed for SQLite desktop apps where database-level locking
    (SELECT FOR UPDATE SKIP LOCKED) is not available.

    The dispatcher loads all pending task IDs into a queue at startup,
    then distributes them to workers in a thread-safe manner.

    Usage:
        # For extraction tasks
        dispatcher = ExtractionTaskDispatcher(uow)
        dispatcher.load_tasks(campaign_id, max_attempts=3)

        # Workers claim tasks
        while task_id := dispatcher.claim_next():
            process_task(task_id)

    Thread Safety:
        - `queue.Queue` is thread-safe by design
        - Multiple workers can safely call `claim_next()` concurrently
        - Each task ID is returned to exactly one worker
    """

    def __init__(self) -> None:
        self._queue: queue.Queue[T] = queue.Queue()
        self._total_loaded: int = 0
        self._lock = threading.Lock()

    def claim_next(self) -> T | None:
        """
        Claim the next task ID from the queue.

        Thread-safe: each call returns a unique task ID.

        Returns:
            Task ID to process, or None if queue is empty.
        """
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def remaining(self) -> int:
        """Get approximate number of tasks remaining in queue."""
        return self._queue.qsize()

    def total_loaded(self) -> int:
        """Get total number of tasks loaded into queue."""
        return self._total_loaded

    def _load_ids(self, task_ids: list[T]) -> int:
        """
        Load task IDs into the queue.

        Returns:
            Number of tasks loaded.
        """
        with self._lock:
            for task_id in task_ids:
                self._queue.put(task_id)
            self._total_loaded = len(task_ids)

        logger.info(
            "tasks_loaded_to_queue",
            total_tasks=len(task_ids),
        )

        return len(task_ids)


class ExtractionTaskDispatcher(TaskDispatcher[ExtractionTaskId]):
    """
    Dispatcher for PlaceExtractionTask processing.

    Loads pending extraction tasks for a specific campaign.
    """

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        super().__init__()
        self._uow = uow

    def load_tasks(
        self,
        campaign_id: CampaignId,
        max_attempts: int = 3,
    ) -> int:
        """
        Load all pending extraction tasks for a campaign into the queue.

        Args:
            campaign_id: Campaign to load tasks from.
            max_attempts: Include FAILED tasks with fewer attempts than this.

        Returns:
            Number of tasks loaded.
        """
        with self._uow:
            task_ids = self._uow.place_extraction_task_repository.find_pending_ids(
                campaign_id=campaign_id,
                max_attempts=max_attempts,
            )

        logger.info(
            "extraction_tasks_loaded",
            campaign_id=str(campaign_id),
            task_count=len(task_ids),
        )

        return self._load_ids(task_ids)


class EnrichmentTaskDispatcher(TaskDispatcher[EnrichmentTaskId]):
    """
    Dispatcher for WebsitePlaceEnrichmentTask processing.

    Loads pending enrichment tasks (global, not campaign-specific).
    """

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        super().__init__()
        self._uow = uow

    def load_tasks(
        self,
        max_attempts: int = 3,
    ) -> int:
        """
        Load all pending enrichment tasks into the queue.

        Args:
            max_attempts: Include FAILED tasks with fewer attempts than this.

        Returns:
            Number of tasks loaded.
        """
        with self._uow:
            task_ids = self._uow.website_enrichment_task_repository.find_pending_ids(
                max_attempts=max_attempts,
            )

        logger.info(
            "enrichment_tasks_loaded",
            task_count=len(task_ids),
        )

        return self._load_ids(task_ids)
