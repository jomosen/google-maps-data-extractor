from typing import Any

from ...domain.enums.campaign_scope import CampaignScope
from ...domain.interfaces.geoname_query_service import GeonameQueryService
from ...domain.value_objects.campaign import CampaignGeonameSelectionParams
from ...domain.value_objects.geo import Geoname


class GeonameSelectionService:
    """
    Application service for selecting geonames based on campaign parameters.

    Orchestrates calls to GeonameQueryService (I/O port) and translates
    domain concepts (scope) into query filters.

    The scope determines the geographical boundary:
    - WORLD: Get cities from all countries
    - COUNTRY: Get cities within the specified country
    - ADMIN1: Get cities within the specified admin1 region
    - ADMIN2: Get cities within the specified admin2 region
    - CITY: Return the specific city (no query needed)
    """

    def __init__(self, geoname_query_service: GeonameQueryService) -> None:
        self._geoname_query_service = geoname_query_service

    def select(self, params: CampaignGeonameSelectionParams) -> list[Geoname]:
        """
        Select geonames (cities) within the scope boundary.

        For CITY scope, returns the city directly.
        For other scopes, queries for cities within the boundary.
        """
        # CITY scope: return the specific city
        if params.scope == CampaignScope.CITY:
            if params.scope_geoname_id is None:
                return []
            return self._geoname_query_service.find_by_geoname_id(
                params.scope_geoname_id
            )

        # Build filters for querying cities within the scope boundary
        filters: dict[str, Any] = {}

        if params.scope == CampaignScope.COUNTRY:
            if params.scope_country_code is not None:
                filters["countryCode"] = params.scope_country_code
        elif params.scope == CampaignScope.ADMIN1:
            if params.scope_geoname_id is not None:
                filters["admin1GeonameId"] = params.scope_geoname_id
        elif params.scope == CampaignScope.ADMIN2:
            if params.scope_geoname_id is not None:
                filters["admin2GeonameId"] = params.scope_geoname_id
        # WORLD scope: no boundary filter, get cities from all countries

        if params.min_population is not None:
            filters["minPopulation"] = params.min_population

        if params.iso_language is not None:
            filters["isoLanguage"] = params.iso_language

        if not filters:
            return []

        return self._geoname_query_service.find_city_geonames(filters)
