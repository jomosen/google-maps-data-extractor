from abc import ABC, abstractmethod
from typing import Any

from ..value_objects.geo import Country, Geoname


class GeonameQueryService(ABC):
    """
    Port for querying geoname data from external sources.

    This is an I/O abstraction. The implementation lives in infrastructure
    and may query an external API (geonames.org) or a local database.
    """

    @abstractmethod
    def find_admin_geonames(self, filters: dict[str, Any]) -> list[Geoname]:
        """
        Find administrative divisions (ADM1, ADM2, ADM3) matching filters.

        Args:
            filters: Query filters (countryCode, featureCode, minPopulation, etc.)

        Returns:
            List of Geoname value objects.
        """
        ...

    @abstractmethod
    def find_city_geonames(self, filters: dict[str, Any]) -> list[Geoname]:
        """
        Find cities/places matching filters.

        Args:
            filters: Query filters (countryCode, minPopulation, etc.)

        Returns:
            List of Geoname value objects.
        """
        ...

    @abstractmethod
    def get_countries(self) -> list[Country]:
        """
        Get all available countries.

        Returns:
            List of Country value objects.
        """
        ...

    @abstractmethod
    def find_by_geoname_id(self, geoname_id: int) -> list[Geoname]:
        """
        Find a specific geoname by its ID.

        Args:
            geoname_id: The geoname ID to look up.

        Returns:
            List containing the Geoname if found, empty list otherwise.
        """
        ...
