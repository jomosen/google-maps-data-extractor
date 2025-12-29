from dataclasses import dataclass
from typing import Optional


@dataclass
class ExtractedPlaceBookingOption:
    
    provider_name: str
    title: str = None

    provider_logo: Optional[str] = None
    image: Optional[str] = None
    price: Optional[str] = None
    info_items: Optional[list[str]] = None