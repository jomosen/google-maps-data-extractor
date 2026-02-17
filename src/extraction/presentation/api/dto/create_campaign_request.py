"""Request DTO for creating campaigns"""
from pydantic import BaseModel, Field, validator
from typing import Optional


class CreateCampaignRequest(BaseModel):
    """
    Request DTO for creating a new campaign.
    
    Validates incoming HTTP request from frontend.
    Maps to CreateCampaignCommand (domain).
    """
    
    # Obligatorios
    activity: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Activity to search (e.g., 'restaurants', 'hotels')",
        example="restaurants"
    )
    country_code: str = Field(
        ...,
        min_length=2,
        max_length=2,
        description="ISO 3166-1 alpha-2 country code",
        example="ES"
    )
    
    # Opcionales - Geographic scope (structured)
    scope: Optional[str] = Field(
        None,
        description="Geographic scope: 'country', 'admin1', 'admin2', 'city'",
        example="city"
    )
    scope_geoname_id: Optional[int] = Field(
        None,
        description="Geoname ID of the selected scope (for admin1/admin2/city)",
        example=3117735
    )
    scope_geoname_name: Optional[str] = Field(
        None,
        max_length=200,
        description="Name of the selected scope location",
        example="Madrid"
    )
    
    # Legacy fields (deprecated but kept for backward compatibility)
    region: Optional[str] = Field(
        None,
        max_length=200,
        description="Region/State name (optional)",
        example="Comunidad de Madrid"
    )
    province: Optional[str] = Field(
        None,
        max_length=200,
        description="Province name (optional)",
        example="Madrid"
    )
    city: Optional[str] = Field(
        None,
        max_length=200,
        description="City name (optional)",
        example="Madrid"
    )
    min_population: Optional[int] = Field(
        15000,
        ge=0,
        description="Minimum population for city selection",
        example=50000
    )
    
    # Opcionales - Extraction configuration
    locale: Optional[str] = Field(
        "en-US",
        description="Locale for extraction",
        example="en-US"
    )
    max_results: Optional[int] = Field(
        50,
        ge=1,
        le=500,
        description="Maximum results per task",
        example=50
    )
    min_rating: Optional[float] = Field(
        4.0,
        ge=0.0,
        le=5.0,
        description="Minimum rating filter",
        example=4.0
    )
    
    @validator('country_code')
    def country_code_uppercase(cls, v):
        """Ensure country code is uppercase."""
        return v.upper()
    
    @validator('activity')
    def activity_not_empty(cls, v):
        """Ensure activity is not just whitespace."""
        if not v.strip():
            raise ValueError("activity cannot be empty or whitespace")
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "activity": "restaurants",
                "country_code": "ES",
                "scope": "city",
                "scope_geoname_id": 3117735,
                "scope_geoname_name": "Madrid",
                "min_population": 50000,
                "locale": "es-ES",
                "max_results": 50,
                "min_rating": 4.0
            }
        }
