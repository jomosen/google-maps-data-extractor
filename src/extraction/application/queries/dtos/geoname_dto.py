"""DTOs for geoname query results."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeonameDto:
    """Result DTO for a geoname (admin division or city)."""

    geoname_id: int
    name: str
    code: str  # admin1_code, admin2_code, or geoname_id as string
    population: int
