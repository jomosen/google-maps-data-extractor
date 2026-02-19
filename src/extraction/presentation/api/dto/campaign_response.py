"""Response DTOs for campaign operations"""
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class CampaignResponse(BaseModel):
    """Response DTO for campaign list view."""

    campaign_id: str = Field(..., example="01ARZ3NDEKTSV4RRFFQ69G5FAV")
    title: str = Field(..., example="Restaurants in Madrid, Spain")
    status: str = Field(..., example="pending")
    total_tasks: int = Field(..., example=10)
    created_at: datetime
    max_bots: int = Field(..., example=30)
    activity: str = Field(..., example="restaurants")
    location_name: str = Field(..., example="Madrid, Spain")


class CampaignDetailResponse(BaseModel):
    """Response DTO for campaign detail view."""

    campaign_id: str
    title: str
    status: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    completion_percentage: float
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    max_bots: int
    activity: str
    location_name: str


class PlaceResponse(BaseModel):
    """Response DTO for extracted place."""

    place_id: str
    name: str | None
    address: str | None
    city: str | None
    rating: float | None
    review_count: int | None
    phone: str | None
    website_link: str | None
    category: str | None


class TaskResponse(BaseModel):
    """Response DTO for extraction task."""

    task_id: str
    search_seed: str
    geoname_name: str
    status: str
    attempts: int
    last_error: str | None
    created_at: datetime
