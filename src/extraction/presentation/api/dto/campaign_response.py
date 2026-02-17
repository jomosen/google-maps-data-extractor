"""Response DTO for campaign operations"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CampaignResponse(BaseModel):
    """
    Response DTO for campaign operations.
    
    Serializes Campaign entity for HTTP response.
    """
    
    campaign_id: str = Field(
        ...,
        description="Unique campaign identifier (ULID)",
        example="01ARZ3NDEKTSV4RRFFQ69G5FAV"
    )
    title: str = Field(
        ...,
        description="Auto-generated campaign title",
        example="Restaurants in Madrid, Spain"
    )
    status: str = Field(
        ...,
        description="Campaign status",
        example="PENDING"
    )
    total_tasks: int = Field(
        ...,
        description="Total number of extraction tasks",
        example=10
    )
    created_at: datetime = Field(
        ...,
        description="Campaign creation timestamp"
    )
    extraction_bots: int = Field(
        ...,
        description="Number of bots allocated for extraction",
        example=3
    )
    
    class Config:
        schema_extra = {
            "example": {
                "campaign_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
                "title": "Restaurants in Madrid, Spain",
                "status": "PENDING",
                "total_tasks": 10,
                "created_at": "2026-02-17T10:30:00Z",
                "extraction_bots": 3
            }
        }
