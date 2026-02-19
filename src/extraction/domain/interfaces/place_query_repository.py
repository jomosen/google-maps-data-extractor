"""Port for querying extracted place data (read-side)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from extraction.application.queries.dtos.place_dto import PlaceDto


class PlaceQueryRepository(ABC):
    """Read-side output port for extracted places."""

    @abstractmethod
    def find_by_campaign(self, campaign_id: str) -> list[PlaceDto]:
        """Retrieve all extracted places for a campaign."""
        ...
