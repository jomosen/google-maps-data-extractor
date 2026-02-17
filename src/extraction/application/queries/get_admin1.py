"""Query handler for fetching Admin1 divisions (states/provinces)."""

from dataclasses import dataclass

from ...domain.interfaces.geoname_query_service import GeonameQueryService
from .dtos import GeonameDTO


@dataclass(frozen=True)
class GetAdmin1Query:
    """Query to get Admin1 divisions for a country."""

    country_code: str


class GetAdmin1Handler:
    """Handler for GetAdmin1Query."""

    def __init__(self, geoname_service: GeonameQueryService) -> None:
        self._geoname_service = geoname_service

    def handle(self, query: GetAdmin1Query) -> list[GeonameDTO]:
        geonames = self._geoname_service.find_admin_geonames({
            "countryCode": query.country_code,
            "featureCode": "ADM1",
        })

        results = [
            GeonameDTO(
                geoname_id=g.geoname_id,
                name=g.name,
                code=g.admin1_code or str(g.geoname_id),
                population=g.population,
            )
            for g in geonames
        ]

        results.sort(key=lambda x: x.name)
        return results
