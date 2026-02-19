"""Query handler for fetching campaign detail."""

from __future__ import annotations

from dataclasses import dataclass

from ...domain.interfaces.campaign_query_repository import CampaignQueryRepository
from .dtos.campaign_dto import CampaignDto


@dataclass(frozen=True)
class GetCampaignByIdQuery:
    campaign_id: str


class GetCampaignByIdHandler:
    def __init__(self, campaign_query_repository: CampaignQueryRepository) -> None:
        self._repository = campaign_query_repository

    def handle(self, query: GetCampaignByIdQuery) -> CampaignDto | None:
        return self._repository.find_by_id(query.campaign_id)
