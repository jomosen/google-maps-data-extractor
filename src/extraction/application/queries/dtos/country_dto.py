"""DTO for country query results."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CountryDto:
    """Application-layer DTO for country list view."""

    code: str
    name: str
    languages: str
    continent: str
    capital: str
    population: int
