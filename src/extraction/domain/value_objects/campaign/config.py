from dataclasses import dataclass, field
from typing import Tuple, Optional

from ...enums.enrichment_type import EnrichmentType
from .geoname_selection_params import CampaignGeonameSelectionParams
from .enrichment_pool_config import EnrichmentPoolConfig


@dataclass(frozen=True)
class CampaignConfig:
    """
    Configuracion de una campaign de extraccion.

    El pipeline es modular y soporta multiples pools de enriquecimiento
    que pueden ejecutarse en paralelo.

    Ejemplo:
        config = CampaignConfig(
            search_seeds=("restaurants",),
            geoname_selection_params=params,
            max_bots=30,
            enrichment_pools=(
                EnrichmentPoolConfig(EnrichmentType.WEBSITE, bots=10),
            ),
        )
    """
    search_seeds: Tuple[str, ...]
    geoname_selection_params: CampaignGeonameSelectionParams
    locale: str = "en-US"
    max_results: int = 50
    min_rating: float = 0
    min_num_reviews: int = 0
    max_reviews: int = 0
    max_bots: int = 10
    enrichment_pools: Tuple[EnrichmentPoolConfig, ...] = field(
        default_factory=lambda: (
            EnrichmentPoolConfig(EnrichmentType.WEBSITE, workers=10),
        )
    )
    max_attempts: int = 10

    def __post_init__(self) -> None:
        # Limpiar seeds
        cleaned_seeds = tuple(
            s.strip() for s in self.search_seeds if s and s.strip()
        )
        object.__setattr__(self, "search_seeds", cleaned_seeds)

        if self.max_results is None:
            object.__setattr__(self, "max_results", 99_999)

        if not 0.0 <= self.min_rating <= 5.0:
            raise ValueError("min_rating must be between 0.0 and 5.0")

        if self.max_bots <= 0:
            raise ValueError("max_bots must be > 0")

        if self.max_attempts <= 0:
            raise ValueError("max_attempts must be > 0")

        # Validar que no hay pools duplicados
        enabled_types = [
            pool.enrichment_type
            for pool in self.enrichment_pools
            if pool.enabled
        ]
        if len(enabled_types) != len(set(enabled_types)):
            raise ValueError("Duplicate enrichment pool types not allowed")

    def get_enrichment_pool(
        self, enrichment_type: EnrichmentType
    ) -> Optional[EnrichmentPoolConfig]:
        """Obtiene la configuracion de un pool de enriquecimiento por tipo."""
        for pool in self.enrichment_pools:
            if pool.enrichment_type == enrichment_type and pool.enabled:
                return pool
        return None

    def get_enabled_enrichment_pools(self) -> Tuple[EnrichmentPoolConfig, ...]:
        """Retorna solo los pools de enriquecimiento habilitados."""
        return tuple(pool for pool in self.enrichment_pools if pool.enabled)
