from dataclasses import dataclass


@dataclass(frozen=True)
class CampaignGeonameSelectionParams:
    """
    Parameters for geoname selection in a campaign.

    Geographic scope is derived from which fields are populated:
    - Only country_code             → all cities in the country
    - + admin1_code                 → cities within that admin1 region
    - + admin2_code                 → cities within that admin2 province
    - + city_geoname_id             → that specific city only

    location_name is a display snapshot built by the frontend in
    reverse specificity order: city → admin2 → admin1 → country.
    Example: "Madrid, Comunidad de Madrid, ES"
    """

    country_code: str
    admin1_code: str | None = None
    admin2_code: str | None = None
    city_geoname_id: int | None = None
    min_population: int = 15000
    iso_language: str | None = None
    location_name: str = ""

    def __post_init__(self) -> None:
        if len(self.country_code) != 2:
            raise ValueError("country_code must be a 2-letter ISO code")
        if self.min_population < 0:
            raise ValueError("min_population must be >= 0")
        if self.admin2_code and not self.admin1_code:
            raise ValueError("admin1_code is required when admin2_code is set")
        if self.city_geoname_id is not None and not self.admin1_code:
            raise ValueError("admin1_code is required when city_geoname_id is set")
