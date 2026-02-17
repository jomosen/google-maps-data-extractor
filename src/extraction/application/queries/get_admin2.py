"""Query handler for fetching Admin2 divisions (counties/districts)."""

from dataclasses import dataclass

from ...domain.interfaces.geoname_query_service import GeonameQueryService
from .dtos import GeonameDTO


@dataclass(frozen=True)
class GetAdmin2Query:
    """Query to get Admin2 divisions for a country and Admin1."""

    country_code: str
    admin1_code: str


class GetAdmin2Handler:
    """Handler for GetAdmin2Query."""

    def __init__(self, geoname_service: GeonameQueryService) -> None:
        self._geoname_service = geoname_service

    def handle(self, query: GetAdmin2Query) -> list[GeonameDTO]:
        geonames = self._geoname_service.find_admin_geonames({
            "countryCode": query.country_code,
            "featureCode": "ADM2",
            "admin1Code": query.admin1_code,
        })

        results = [
            GeonameDTO(
                geoname_id=g.geoname_id,
                name=g.name,
                code=g.admin2_code or str(g.geoname_id),
                population=g.population,
            )
            for g in geonames
        ]

        results.sort(key=lambda x: x.name)
        return results
