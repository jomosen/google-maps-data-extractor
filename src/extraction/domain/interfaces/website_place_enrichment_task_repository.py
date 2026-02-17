from abc import ABC, abstractmethod
from typing import Optional

from ..entities.place_website_enrichment_task import WebsitePlaceEnrichmentTask
from ..value_objects.ids import EnrichmentTaskId


class WebsitePlaceEnrichmentTaskRepository(ABC):
    """
    Persistence port for WebsitePlaceEnrichmentTask.

    This is a DOMAIN repository for WRITE operations:
    - save (persist enrichment task)
    - find_by_id (load task for modification)
    - claim_next_pending (claim next task atomically)
    - find_pending_ids (get all pending task IDs for queue loading)

    Enrichment tasks are GLOBAL (not tied to a specific campaign),
    as they are created when places with websites are extracted.
    """

    @abstractmethod
    def save(self, task: WebsitePlaceEnrichmentTask) -> None:
        """Persist the enrichment task (insert or update)."""
        ...

    @abstractmethod
    def find_by_id(self, task_id: EnrichmentTaskId) -> Optional[WebsitePlaceEnrichmentTask]:
        """Load task for modification."""
        ...

    @abstractmethod
    def claim_next_pending(
        self,
        max_attempts: int,
    ) -> Optional[WebsitePlaceEnrichmentTask]:
        """
        Claim the next pending enrichment task for processing.

        Unlike PlaceExtractionTaskRepository, does not require campaign_id
        because enrichment tasks are global.

        Transitions the task from PENDING/FAILED -> IN_PROGRESS.

        Note: For SQLite desktop apps with multiple workers, use
        TaskDispatcher instead of calling this method directly.

        Args:
            max_attempts: Maximum retry attempts allowed.

        Returns:
            The claimed task (now IN_PROGRESS), or None if no tasks available.
        """
        ...

    @abstractmethod
    def find_pending_ids(
        self,
        max_attempts: int,
    ) -> list[EnrichmentTaskId]:
        """
        Get all pending enrichment task IDs.

        Used by TaskDispatcher to load tasks into the in-memory queue.
        Includes FAILED tasks that haven't exceeded max_attempts.

        Args:
            max_attempts: Maximum retry attempts allowed.

        Returns:
            List of task IDs that are available for processing.
        """
        ...
