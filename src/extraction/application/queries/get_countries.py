"""Query handler for fetching available countries."""

from __future__ import annotations

from dataclasses import dataclass

from ...domain.interfaces.geoname_query_service import GeonameQueryService
from .dtos.country_dto import CountryDto


@dataclass(frozen=True)
class GetCountriesQuery:
    """Query to get all available countries. No parameters needed."""
    pass


class GetCountriesHandler:
    """Handler for GetCountriesQuery."""

    def __init__(self, geoname_service: GeonameQueryService) -> None:
        self._geoname_service = geoname_service

    def handle(self, query: GetCountriesQuery) -> list[CountryDto]:
        countries = self._geoname_service.get_countries()
        results = [
            CountryDto(
                code=c.iso_alpha2,
                name=c.country_name,
                languages=c.languages,
                continent=c.continent,
                capital=c.capital,
                population=c.population,
            )
            for c in countries
        ]
        results.sort(key=lambda c: c.name)
        return results
