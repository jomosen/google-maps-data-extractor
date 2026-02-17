from abc import ABC, abstractmethod
from typing import Optional

from ..entities.place_extraction_task import PlaceExtractionTask
from ..value_objects.ids import CampaignId, ExtractionTaskId


class PlaceExtractionTaskRepository(ABC):
    """
    Persistence port for PlaceExtractionTask.

    This is a DOMAIN repository for WRITE operations:
    - save (persist task)
    - find_by_id (load task for modification)
    - claim_next_pending (claim next task atomically)
    - find_pending_ids (get all pending task IDs for queue loading)

    For READ operations (list tasks, statistics),
    use TaskQueryRepositoryPort in the application layer.
    """

    @abstractmethod
    def save(self, task: PlaceExtractionTask) -> None:
        """Persist the task (insert or update)."""
        ...

    @abstractmethod
    def find_by_id(self, task_id: ExtractionTaskId) -> Optional[PlaceExtractionTask]:
        """Load task for modification."""
        ...

    @abstractmethod
    def claim_next_pending(
        self,
        campaign_id: CampaignId,
        max_attempts: int,
    ) -> Optional[PlaceExtractionTask]:
        """
        Claim the next pending task for processing.

        Transitions the task from PENDING/FAILED -> IN_PROGRESS.

        Note: For SQLite desktop apps with multiple workers, use
        TaskDispatcher instead of calling this method directly.

        Args:
            campaign_id: Campaign ID to claim tasks from.
            max_attempts: Maximum retry attempts allowed.

        Returns:
            The claimed task (now IN_PROGRESS), or None if no tasks available.
        """
        ...

    @abstractmethod
    def find_pending_ids(
        self,
        campaign_id: CampaignId,
        max_attempts: int,
    ) -> list[ExtractionTaskId]:
        """
        Get all pending task IDs for a campaign.

        Used by TaskDispatcher to load tasks into the in-memory queue.
        Includes FAILED tasks that haven't exceeded max_attempts.

        Args:
            campaign_id: Campaign ID to get tasks from.
            max_attempts: Maximum retry attempts allowed.

        Returns:
            List of task IDs that are available for processing.
        """
        ...
