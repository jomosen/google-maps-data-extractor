"""Query handler for fetching extracted places for a campaign."""

from __future__ import annotations

from dataclasses import dataclass

from ...domain.interfaces.place_query_repository import PlaceQueryRepository
from .dtos.place_dto import PlaceDto


@dataclass(frozen=True)
class GetCampaignPlacesQuery:
    campaign_id: str


class GetCampaignPlacesHandler:
    def __init__(self, place_query_repository: PlaceQueryRepository) -> None:
        self._repository = place_query_repository

    def handle(self, query: GetCampaignPlacesQuery) -> list[PlaceDto]:
        return self._repository.find_by_campaign(query.campaign_id)
