from dataclasses import dataclass

from ...enums.campaign_scope import CampaignScope


@dataclass(frozen=True)
class CampaignGeonameSelectionParams:
    """
    Parameters for geoname selection in a campaign.

    The scope is derived from the form selection:
    - All Countries → WORLD
    - Specific country → COUNTRY
    - Specific admin1 → ADMIN1
    - Specific admin2 → ADMIN2
    - Specific city → CITY

    When scope is COUNTRY/ADMIN1/ADMIN2/CITY, scope_geoname_id identifies
    the specific selected location.
    """

    scope: CampaignScope = CampaignScope.COUNTRY
    scope_country_code: str | None = None
    scope_geoname_id: int | None = None
    scope_geoname_name: str | None = None
    min_population: int = 15000
    iso_language: str | None = None

    def __post_init__(self) -> None:
        if self.min_population < 0:
            raise ValueError("min_population must be >= 0")
        if self.scope_country_code and len(self.scope_country_code) != 2:
            raise ValueError("scope_country_code must be a 2-letter ISO code")
        # Validate scope requirements
        if self.scope == CampaignScope.COUNTRY:
            # Country scope requires country_code
            if self.scope_country_code is None:
                raise ValueError("scope_country_code is required for COUNTRY scope")
        elif self.scope_geoname_id is None:
            # Other scopes (ADMIN1, ADMIN2, CITY) require geoname_id
            raise ValueError(
                f"scope_geoname_id is required for scope {self.scope.value}"
            )
