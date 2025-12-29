from dataclasses import dataclass


@dataclass(frozen=True)
class PlaceExtractionTaskGeoname:

    name: str
    latitude: float
    longitude: float
