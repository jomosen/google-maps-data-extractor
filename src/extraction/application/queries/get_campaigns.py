"""Query handler for fetching campaign list."""

from __future__ import annotations

from dataclasses import dataclass

from ...domain.interfaces.campaign_query_repository import CampaignQueryRepository
from .dtos.campaign_dto import CampaignDto


@dataclass(frozen=True)
class GetCampaignsQuery:
    """Query to retrieve all campaigns. No parameters needed."""
    pass


class GetCampaignsHandler:
    """Handler for GetCampaignsQuery. Delegates directly to the query repository."""

    def __init__(self, campaign_query_repository: CampaignQueryRepository) -> None:
        self._repository = campaign_query_repository

    def handle(self, query: GetCampaignsQuery) -> list[CampaignDto]:
        return self._repository.find_all()
