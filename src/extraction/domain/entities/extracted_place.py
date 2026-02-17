from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
from ..value_objects.place import (
    ExtractedPlaceBookingOption as BookingOption,
    ExtractedPlaceAttributes as Attributes,
    ExtractedPlaceHours as Hours,
    PlaceEnrichment,
)
from ..value_objects.ids import PlaceId, ExtractionTaskId
from .extracted_place_review import ExtractedPlaceReview as Review
from ..enums.enrichment_status import EnrichmentStatus


@dataclass
class ExtractedPlace:

    place_id: PlaceId

    name: Optional[str] = None
    cid: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    state_code: Optional[str] = None
    postal_code: Optional[str] = None
    review_count: Optional[int] = None
    rating: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    plus_code: Optional[str] = None
    category: Optional[str] = None
    website_link: Optional[str] = None
    menu_link: Optional[str] = None
    appointment_link: Optional[str] = None
    booking_link: Optional[str] = None
    order_online_link: Optional[str] = None
    domain: Optional[str] = None
    main_image: Optional[str] = None
    attributes: Optional[Attributes] = None
    description: Optional[str] = None
    hours: Optional[Hours] = None
    reviews: List[Review] = field(default_factory=list)
    review_summary: List[str] = field(default_factory=list)
    closure_status: Optional[str] = None
    claimable: Optional[bool] = False
    average_price: Optional[str] = None
    booking_options: List[BookingOption] = field(default_factory=list)
    task_id: Optional[ExtractionTaskId] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    # Enrichment tracking
    enrichment_status: EnrichmentStatus = EnrichmentStatus.NONE

    # Polymorphic collection
    enrichments: List[PlaceEnrichment] = field(default_factory=list)
