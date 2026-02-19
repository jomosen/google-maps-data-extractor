"""Query handler for fetching extraction tasks for a campaign."""

from __future__ import annotations

from dataclasses import dataclass

from ...domain.interfaces.task_query_repository import TaskQueryRepository
from .dtos.task_dto import TaskDto


@dataclass(frozen=True)
class GetCampaignTasksQuery:
    campaign_id: str


class GetCampaignTasksHandler:
    def __init__(self, task_query_repository: TaskQueryRepository) -> None:
        self._repository = task_query_repository

    def handle(self, query: GetCampaignTasksQuery) -> list[TaskDto]:
        return self._repository.find_by_campaign(query.campaign_id)
