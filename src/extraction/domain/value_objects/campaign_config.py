from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any

from extraction.domain.value_objects.campaign_geoname_selection_params import GeoNameSelectionParamsForExtractionJob


@dataclass(frozen=True)
class CampaignConfig:
    search_seeds: Tuple[str, ...]
    geoname_selection_params: GeoNameSelectionParamsForExtractionJob
    locale: str = "en-US"
    max_results: int = 50
    min_rating: float = 4.0
    min_num_reviews: int = 0
    max_reviews: int = 0
    max_workers: int = 30
    max_attempts: int = 10

    def __post_init__(self) -> None:

        cleaned_seeds = tuple(
            s.strip() for s in self.search_seeds if s and s.strip()
        )
        object.__setattr__(self, "search_seeds", cleaned_seeds)

        if self.max_results is None:
            object.__setattr__(self, "max_results", 99_999)

        if self.geoname_selection_params.min_population < 0:
            raise ValueError("min_population must be >= 0")

        if not 0.0 <= self.min_rating <= 5.0:
            raise ValueError("min_rating must be between 0.0 and 5.0")

        if self.max_workers <= 0:
            raise ValueError("max_workers must be > 0")

        if self.max_attempts <= 0:
            raise ValueError("max_attempts_per_task must be > 0")