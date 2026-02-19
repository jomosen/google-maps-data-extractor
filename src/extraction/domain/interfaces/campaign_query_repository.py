"""Port for querying campaign data (read-side)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from extraction.application.queries.dtos.campaign_dto import CampaignDto


class CampaignQueryRepository(ABC):
    """
    Read-side output port (secondary port).

    The implementation lives in infrastructure and queries the persistence
    store directly without loading full Campaign aggregates.
    Returns DTOs directly — no domain entity reconstruction needed.
    """

    @abstractmethod
    def find_all(self) -> list[CampaignDto]:
        """Retrieve all campaigns as DTOs ordered by creation date descending."""
        ...

    @abstractmethod
    def find_by_id(self, campaign_id: str) -> CampaignDto | None:
        """Retrieve campaign detail by ID, or None if not found."""
        ...
