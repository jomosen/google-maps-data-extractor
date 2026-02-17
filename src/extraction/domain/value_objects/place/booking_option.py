from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ExtractedPlaceBookingOption:

    provider_name: str
    title: Optional[str] = None

    provider_logo: Optional[str] = None
    image: Optional[str] = None
    price: Optional[str] = None
    info_items: Optional[tuple[str, ...]] = None
