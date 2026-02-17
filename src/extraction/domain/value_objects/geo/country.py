from dataclasses import dataclass


@dataclass(frozen=True)
class Country:

    geoname_id: int
    iso_alpha2: str
    country_name: str
    continent: str
    capital: str
    population: int
    languages: str
