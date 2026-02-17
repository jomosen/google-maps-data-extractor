from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Geoname:
    """
    Value object representing a geographic location from GeoNames.

    Used for administrative divisions (ADM1, ADM2, etc.) and cities.
    """

    geoname_id: int
    name: str
    latitude: float
    longitude: float
    country_code: str
    population: int
    feature_code: Optional[str] = None
    admin1_code: Optional[str] = None
    admin2_code: Optional[str] = None
    postal_code_regex: Optional[str] = None
    country_name: Optional[str] = None
    admin1_name: Optional[str] = None
