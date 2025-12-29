from abc import ABC
from dataclasses import dataclass, field
import datetime
from typing import List, Optional

@dataclass
class PlaceEnrichment(ABC):
    extracted_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

@dataclass
class WebsitePlaceEnrichment(PlaceEnrichment):
    title: Optional[str] = None
    description: Optional[str] = None
    meta_keywords: List[str] = field(default_factory=list)
    emails: List[str] = field(default_factory=list)
    social_urls: List[str] = field(default_factory=list)