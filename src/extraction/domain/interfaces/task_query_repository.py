"""Port for querying extraction task data (read-side)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from extraction.application.queries.dtos.task_dto import TaskDto


class TaskQueryRepository(ABC):
    """Read-side output port for extraction tasks."""

    @abstractmethod
    def find_by_campaign(self, campaign_id: str) -> list[TaskDto]:
        """Retrieve all tasks for a campaign."""
        ...
