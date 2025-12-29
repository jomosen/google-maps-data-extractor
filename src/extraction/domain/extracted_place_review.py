from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class ExtractedPlaceReview:
    
    id: str
    place_id: str
    rating: Optional[float] = None
    author: Optional[str] = None
    text: Optional[str] = None
    lang: Optional[str] = None
    photos: Optional[List[str]] = None
    created_at: Optional[datetime] = None
