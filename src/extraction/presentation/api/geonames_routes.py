"""
REST API endpoints for geonames data.

Exposes geographic data (countries, regions, provinces, cities) to the frontend
through proxy endpoints that delegate to application layer query handlers.
"""

import os
from fastapi import APIRouter, Query as QueryParam
from typing import List

from ...application.queries.get_countries import (
    GetCountriesQuery,
    GetCountriesHandler,
    CountryDto,
)
from ...application.queries.get_admin1 import (
    GetAdmin1Query,
    GetAdmin1Handler,
)
from ...application.queries.get_admin2 import (
    GetAdmin2Query,
    GetAdmin2Handler,
)
from ...application.queries.get_cities import (
    GetCitiesQuery,
    GetCitiesHandler,
)
from ...application.queries.dtos import GeonameDto
from ...infrastructure.http.geoname_query_service import HttpGeonameQueryService


router = APIRouter(prefix="/api/geonames", tags=["geonames"])


# Dependency: Geoname service instance
def get_geoname_service() -> HttpGeonameQueryService:
    """Create geoname service instance."""
    base_url = os.getenv("GEONAMES_API_URL", "http://localhost:8080")
    return HttpGeonameQueryService(base_url=base_url)


@router.get("/countries", response_model=List[CountryDto])
async def get_countries() -> List[CountryDto]:
    """
    Get all available countries.
    
    Returns list of countries with code, name, continent, capital, and population.
    """
    service = get_geoname_service()
    handler = GetCountriesHandler(geoname_service=service)
    query = GetCountriesQuery()
    
    return handler.handle(query)


@router.get("/countries/{country_code}/regions", response_model=List[GeonameDto])
async def get_regions(country_code: str) -> List[GeonameDto]:
    """
    Get Admin1 divisions (regions/states) for a country.
    
    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g., 'ES', 'US')
    
    Returns list of regions with geoname_id, name, code, and population.
    """
    service = get_geoname_service()
    handler = GetAdmin1Handler(geoname_service=service)
    query = GetAdmin1Query(country_code=country_code.upper())
    
    return handler.handle(query)


@router.get("/countries/{country_code}/provinces", response_model=List[GeonameDto])
async def get_provinces(
    country_code: str,
    admin1_code: str = QueryParam(..., description="Admin1 code (region)")
) -> List[GeonameDto]:
    """
    Get Admin2 divisions (provinces/counties) for a country and region.
    
    Args:
        country_code: ISO 3166-1 alpha-2 country code
        admin1_code: Admin1 code from regions endpoint
    
    Returns list of provinces with geoname_id, name, code, and population.
    """
    service = get_geoname_service()
    handler = GetAdmin2Handler(geoname_service=service)
    query = GetAdmin2Query(
        country_code=country_code.upper(),
        admin1_code=admin1_code
    )
    
    return handler.handle(query)


@router.get("/countries/{country_code}/cities", response_model=List[GeonameDto])
async def get_cities(
    country_code: str,
    admin1_code: str | None = QueryParam(None, description="Admin1 code (region)"),
    admin2_code: str | None = QueryParam(None, description="Admin2 code (province)"),
    min_population: int = QueryParam(0, ge=0, description="Minimum population filter")
) -> List[GeonameDto]:
    """
    Get cities for a country, optionally filtered by region/province.
    
    Args:
        country_code: ISO 3166-1 alpha-2 country code
        admin1_code: Optional Admin1 code to filter by region
        admin2_code: Optional Admin2 code to filter by province
        min_population: Minimum population threshold (default: 0)
    
    Returns list of cities with geoname_id, name, code, and population.
    """
    service = get_geoname_service()
    handler = GetCitiesHandler(geoname_service=service)
    query = GetCitiesQuery(
        country_code=country_code.upper(),
        admin1_code=admin1_code,
        admin2_code=admin2_code,
        min_population=min_population
    )
    
    return handler.handle(query)
