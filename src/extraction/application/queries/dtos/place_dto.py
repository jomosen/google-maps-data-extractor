"""DTO for extracted place list view."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PlaceDto:
    """Application-layer DTO for extracted place list view."""

    place_id: str
    name: str | None
    address: str | None
    city: str | None
    rating: float | None
    review_count: int | None
    phone: str | None
    website_link: str | None
    category: str | None
