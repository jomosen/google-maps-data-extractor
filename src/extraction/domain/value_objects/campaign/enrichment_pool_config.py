from dataclasses import dataclass

from ...enums.enrichment_type import EnrichmentType


@dataclass(frozen=True)
class EnrichmentPoolConfig:
    """
    Configuracion de un pool de enriquecimiento del pipeline.

    Cada pool de enriquecimiento tiene:
    - enrichment_type: Tipo de enriquecimiento (WEBSITE, SOCIAL, GBP, etc.)
    - bots: Numero de bots concurrentes para este pool
    - enabled: Si el pool esta habilitado o no

    Ejemplo de uso:
        # Pool independiente (puede empezar inmediatamente)
        website_pool = EnrichmentPoolConfig(
            enrichment_type=EnrichmentType.WEBSITE,
            bots=10,
        )

    """
    enrichment_type: EnrichmentType
    bots: int
    enabled: bool = True

    def __post_init__(self) -> None:
        if self.bots < 0:
            raise ValueError(f"bots must be >= 0, got {self.bots}")
        if self.enabled and self.bots == 0:
            raise ValueError(
                f"Enabled pool {self.enrichment_type.value} must have at least 1 bot"
            )
