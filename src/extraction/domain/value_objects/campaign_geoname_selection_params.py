from dataclasses import dataclass

from extraction.domain.enums.campaign_depth_level import CampaignDepthLevel
from extraction.domain.enums.campaign_scope import CampaignScope


@dataclass(frozen=True)
class CampaignGeonameSelectionParams:
    scope: CampaignScope = CampaignScope.COUNTRY
    scope_geoname_id: int | None = None
    scope_geoname_name: str | None = None
    depth_level: CampaignDepthLevel = CampaignDepthLevel.ADMIN1
    min_population: int = 15000
    iso_language: str | None = None