from typing import Any

from ..interfaces.geoname_query_service import GeonameQueryService
from ..value_objects.campaign import CampaignGeonameSelectionParams
from ..value_objects.geo import Geoname


class GeonameSelectionService:
    """
    Domain service for selecting cities based on campaign geographic params.

    Translates the campaign's geographic scope (derived from which admin
    codes are set) into queries against the GeonameQueryService output port.

    Selection rules (in priority order):
    - city_geoname_id set  → query within scope, return that specific city
    - admin2_code set      → all cities within that admin2 province
    - admin1_code set      → all cities within that admin1 region
    - country_code only    → all cities in the country

    min_population is applied for all scopes except city_geoname_id (where
    the specific city is looked up regardless of population).
    """

    def __init__(self, geoname_query_service: GeonameQueryService) -> None:
        self._geoname_query_service = geoname_query_service

    def select(self, params: CampaignGeonameSelectionParams) -> list[Geoname]:
        """Return the list of cities matching the campaign's geographic scope."""
        filters: dict[str, Any] = {
            "countryCode": params.country_code,
        }

        if params.admin1_code:
            filters["admin1Code"] = params.admin1_code

        if params.admin2_code:
            filters["admin2Code"] = params.admin2_code

        if params.iso_language:
            filters["isoLanguage"] = params.iso_language

        # City scope: find specific city by geoname_id within the known scope.
        # No min_population filter — we want the city regardless of size.
        if params.city_geoname_id is not None:
            cities = self._geoname_query_service.find_city_geonames(filters)
            return [c for c in cities if c.geoname_id == params.city_geoname_id]

        filters["minPopulation"] = params.min_population

        return self._geoname_query_service.find_city_geonames(filters)
