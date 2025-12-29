from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Geoname:
    
    name: str
    latitude: float
    longitude: float
    country_code: str
    population: int
    postal_code_regex: Optional[str] = None
    country_name: Optional[str] = None
    admin1_name: Optional[str] = None
