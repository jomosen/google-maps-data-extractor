"""Request DTO for creating campaigns."""
from typing import Optional

from pydantic import BaseModel, Field, validator


class CreateCampaignRequest(BaseModel):
    """
    Request DTO for creating a new campaign.

    Validates the incoming HTTP request from the frontend.
    Maps to CreateCampaignCommand (domain).

    Geographic scope is derived from which admin fields are populated:
    - Only country_code             → all cities in the country
    - + admin1_code                 → cities within that admin1 region
    - + admin2_code                 → cities within that admin2 province
    - + city_geoname_id             → that specific city only
    """

    # Required
    activity: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Activity to search (e.g., 'restaurants', 'hotels')",
        example="restaurants",
    )
    country_code: str = Field(
        ...,
        min_length=2,
        max_length=2,
        description="ISO 3166-1 alpha-2 country code",
        example="ES",
    )

    # Geographic scope (optional, increasingly specific)
    admin1_code: Optional[str] = Field(
        None,
        max_length=10,
        description="Admin1 region code (e.g., 'MD' for Comunidad de Madrid)",
        example="MD",
    )
    admin2_code: Optional[str] = Field(
        None,
        max_length=10,
        description="Admin2 province code (e.g., '28' for Madrid province)",
        example="28",
    )
    city_geoname_id: Optional[int] = Field(
        None,
        description="Geoname ID of the specific city selected",
        example=3117735,
    )

    # Display snapshot (built by frontend: city → admin2 → admin1 → country)
    location_name: str = Field(
        "",
        max_length=300,
        description="Human-readable location snapshot for display and title generation",
        example="Madrid, Comunidad de Madrid, ES",
    )

    # Language derived from country on the frontend
    iso_language: Optional[str] = Field(
        None,
        max_length=10,
        description="ISO language code for alternate name preference (e.g., 'es')",
        example="es",
    )

    @validator("country_code")
    def country_code_uppercase(cls, v: str) -> str:
        return v.upper()

    @validator("activity")
    def activity_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("activity cannot be empty or whitespace")
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "activity": "restaurants",
                "country_code": "ES",
                "admin1_code": "MD",
                "admin2_code": None,
                "city_geoname_id": None,
                "location_name": "Comunidad de Madrid, ES",
                "iso_language": "es",
            }
        }
