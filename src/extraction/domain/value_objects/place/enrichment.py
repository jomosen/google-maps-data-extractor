from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class PlaceEnrichment(ABC):
    extracted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class WebsitePlaceEnrichment(PlaceEnrichment):
    title: Optional[str] = None
    description: Optional[str] = None
    meta_keywords: tuple[str, ...] = field(default_factory=tuple)
    emails: tuple[str, ...] = field(default_factory=tuple)
    social_urls: tuple[str, ...] = field(default_factory=tuple)
