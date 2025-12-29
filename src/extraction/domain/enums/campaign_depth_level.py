from enum import Enum


class CampaignDepthLevel(str, Enum):
    ADMIN1 = "admin1"
    ADMIN2 = "admin2"
    ADMIN3 = "admin3"
    CITY = "city"