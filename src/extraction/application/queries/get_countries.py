"""
Query handler for fetching available countries.

This query returns all countries available for campaign targeting,
delegating to the GeonameQueryService port.
"""

from __future__ import annotations

from dataclasses import dataclass

from ...domain.interfaces.geoname_query_service import GeonameQueryService
from ...domain.value_objects.geo import Country


@dataclass(frozen=True)
class GetCountriesQuery:
    """
    Query to get all available countries.

    This is a marker class - no parameters needed for this query.
    """
    pass


@dataclass(frozen=True)
class CountryResult:
    """
    Result DTO for a single country.

    Flattens the domain Country value object for presentation layer.
    """
    code: str
    name: str
    languages: str
    continent: str
    capital: str
    population: int

    @classmethod
    def from_domain(cls, country: Country) -> "CountryResult":
        """Create from domain Country value object."""
        return cls(
            code=country.iso_alpha2,
            name=country.country_name,
            languages=country.languages,
            continent=country.continent,
            capital=country.capital,
            population=country.population,
        )


class GetCountriesHandler:
    """
    Handler for GetCountriesQuery.

    Fetches countries from the GeonameQueryService port and transforms
    them into presentation-friendly DTOs.
    """

    def __init__(self, geoname_service: GeonameQueryService) -> None:
        """
        Args:
            geoname_service: Port for querying geoname data.
        """
        self._geoname_service = geoname_service

    def handle(self, query: GetCountriesQuery) -> list[CountryResult]:
        """
        Execute the query.

        Args:
            query: The query (no parameters).

        Returns:
            List of CountryResult DTOs sorted by name.
        """
        countries = self._geoname_service.get_countries()

        results = [
            CountryResult.from_domain(country)
            for country in countries
        ]

        # Sort by country name for consistent presentation
        results.sort(key=lambda c: c.name)

        return results
