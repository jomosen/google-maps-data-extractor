from enum import Enum


class CampaignScope(str, Enum):
    COUNTRY = "country"
    ADMIN1 = "admin1"
    ADMIN2 = "admin2"
    CITY = "city"