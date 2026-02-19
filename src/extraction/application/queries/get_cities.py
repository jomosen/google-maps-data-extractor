"""Query handler for fetching cities."""

from dataclasses import dataclass

from ...domain.interfaces.geoname_query_service import GeonameQueryService
from .dtos import GeonameDto


@dataclass(frozen=True)
class GetCitiesQuery:
    """Query to get cities for a country, optionally filtered by admin divisions."""

    country_code: str
    admin1_code: str | None = None
    admin2_code: str | None = None
    min_population: int = 0


class GetCitiesHandler:
    """Handler for GetCitiesQuery."""

    def __init__(self, geoname_service: GeonameQueryService) -> None:
        self._geoname_service = geoname_service

    def handle(self, query: GetCitiesQuery) -> list[GeonameDto]:
        filters = {
            "countryCode": query.country_code,
            "minPopulation": query.min_population,
        }
        if query.admin1_code:
            filters["admin1Code"] = query.admin1_code
        if query.admin2_code:
            filters["admin2Code"] = query.admin2_code

        geonames = self._geoname_service.find_city_geonames(filters)

        results = [
            GeonameDto(
                geoname_id=g.geoname_id,
                name=g.name,
                code=str(g.geoname_id),
                population=g.population,
            )
            for g in geonames
        ]

        results.sort(key=lambda x: x.name)
        return results
