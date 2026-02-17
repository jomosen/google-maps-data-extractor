from __future__ import annotations

from typing import Any

import requests

from ...domain.interfaces.geoname_query_service import GeonameQueryService
from ...domain.value_objects.geo import Country, Geoname


class HttpGeonameQueryService(GeonameQueryService):
    """
    HTTP implementation of GeonameQueryService.

    Queries the geonames microservice via REST API.
    """

    def __init__(self, base_url: str, timeout: int = 30) -> None:
        """
        Args:
            base_url: Base URL of the geonames microservice (e.g., "http://localhost:8000")
            timeout: Request timeout in seconds
        """
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def find_admin_geonames(self, filters: dict[str, Any]) -> list[Geoname]:
        """
        Find administrative divisions (ADM1, ADM2, ADM3) matching filters.

        Maps domain filters to API query parameters:
        - countryCode → path parameter
        - featureCode → feature_code query param
        - minPopulation → min_population query param (not supported by this endpoint)
        - isoLanguage → language query param
        """
        country_code = filters.get("countryCode")
        if not country_code:
            return []

        url = f"{self._base_url}/countries/{country_code}/admin-divisions"

        params: dict[str, Any] = {
            "limit": 1000,
        }

        if filters.get("featureCode"):
            params["feature_code"] = filters["featureCode"]

        if filters.get("admin1Code"):
            params["admin1_code"] = filters["admin1Code"]

        if filters.get("isoLanguage"):
            params["expand"] = "alternateName"
            params["language"] = filters["isoLanguage"]

        response = requests.get(url, params=params, timeout=self._timeout)
        response.raise_for_status()

        return [self._map_admin_to_geoname(item, country_code) for item in response.json()]

    def find_city_geonames(self, filters: dict[str, Any]) -> list[Geoname]:
        """
        Find cities/places matching filters.

        Maps domain filters to API query parameters:
        - countryCode → path parameter
        - minPopulation → min_population query param
        - isoLanguage → language query param
        """
        country_code = filters.get("countryCode")
        if not country_code:
            return []

        url = f"{self._base_url}/countries/{country_code}/cities"

        params: dict[str, Any] = {
            "limit": 1000,
        }

        if filters.get("minPopulation"):
            params["min_population"] = filters["minPopulation"]

        if filters.get("admin1Code"):
            params["admin1_code"] = filters["admin1Code"]

        if filters.get("admin2Code"):
            params["admin2_code"] = filters["admin2Code"]

        if filters.get("isoLanguage"):
            params["language"] = filters["isoLanguage"]

        response = requests.get(url, params=params, timeout=self._timeout)
        response.raise_for_status()

        return [self._map_city_to_geoname(item, country_code) for item in response.json()]

    def _map_admin_to_geoname(self, data: dict[str, Any], country_code: str) -> Geoname:
        """Map API admin division response to Geoname value object."""
        return Geoname(
            geoname_id=int(data.get("geoname_id", 0)),
            name=data.get("name") or data.get("asciiname", ""),
            latitude=float(data.get("latitude", 0)),
            longitude=float(data.get("longitude", 0)),
            country_code=country_code,
            population=int(data.get("population", 0)),
            feature_code=data.get("feature_code"),
            admin1_code=data.get("admin1_code"),
            admin2_code=data.get("admin2_code"),
            postal_code_regex=None,
            country_name=data.get("country_name"),
            admin1_name=data.get("admin1_name"),
        )

    def _map_city_to_geoname(self, data: dict[str, Any], country_code: str) -> Geoname:
        """Map API city response to Geoname value object."""
        return Geoname(
            geoname_id=int(data.get("geoname_id", 0)),
            name=data.get("name") or data.get("asciiname", ""),
            latitude=float(data.get("latitude", 0)),
            longitude=float(data.get("longitude", 0)),
            country_code=country_code,
            population=int(data.get("population", 0)),
            feature_code=data.get("feature_code"),
            admin1_code=data.get("admin1_code"),
            admin2_code=data.get("admin2_code"),
            postal_code_regex=None,
            country_name=data.get("country_name"),
            admin1_name=data.get("admin1_name"),
        )

    def get_countries(self) -> list[Country]:
        """Get all available countries from the API."""
        url = f"{self._base_url}/countries"

        response = requests.get(url, timeout=self._timeout)
        response.raise_for_status()

        return [self._map_to_country(item) for item in response.json()]

    def _map_to_country(self, data: dict[str, Any]) -> Country:
        """Map API country response to Country value object."""
        return Country(
            geoname_id=int(data.get("geoname_id", 0)),
            iso_alpha2=data.get("iso_alpha2", ""),
            country_name=data.get("country_name", ""),
            continent=data.get("continent", ""),
            capital=data.get("capital", ""),
            population=int(data.get("population", 0)),
            languages=data.get("languages", ""),
        )

    def find_by_geoname_id(self, geoname_id: int) -> list[Geoname]:
        """
        Find a specific geoname by its ID.
        
        Note: This endpoint may not be available in the geonames microservice yet.
        Returns empty list if not found or not implemented.
        """
        # TODO: Implement when geonames microservice adds GET /geonames/{id} endpoint
        # For now, return empty list as this is not critical for campaign creation
        return []
