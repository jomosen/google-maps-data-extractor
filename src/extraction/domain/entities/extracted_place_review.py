from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from ..value_objects.ids import ReviewId, PlaceId


@dataclass
class ExtractedPlaceReview:

    id: ReviewId
    place_id: PlaceId
    rating: Optional[float] = None
    author: Optional[str] = None
    text: Optional[str] = None
    lang: Optional[str] = None
    photos: Optional[List[str]] = None
    created_at: Optional[datetime] = None
