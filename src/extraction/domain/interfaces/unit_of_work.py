from __future__ import annotations

from abc import ABC, abstractmethod

from typing_extensions import Self

from .campaign_repository import CampaignRepository
from .extracted_place_repository import ExtractedPlaceRepository
from .place_extraction_task_repository import PlaceExtractionTaskRepository
from .website_place_enrichment_task_repository import WebsitePlaceEnrichmentTaskRepository


class AbstractUnitOfWork(ABC):
    campaign_repository: CampaignRepository
    extracted_place_repository: ExtractedPlaceRepository
    place_extraction_task_repository: PlaceExtractionTaskRepository
    website_enrichment_task_repository: WebsitePlaceEnrichmentTaskRepository

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...

    @abstractmethod
    def __enter__(self) -> Self: ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...
