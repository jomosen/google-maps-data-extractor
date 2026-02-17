"""
Mappers for converting between domain entities and ORM models.

These functions handle the translation layer between the domain model
(pure Python dataclasses) and the persistence model (SQLAlchemy ORM).
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from ....domain.entities.campaign import Campaign
from ....domain.entities.extracted_place import ExtractedPlace
from ....domain.entities.extracted_place_review import ExtractedPlaceReview
from ....domain.entities.place_extraction_task import PlaceExtractionTask
from ....domain.entities.place_website_enrichment_task import WebsitePlaceEnrichmentTask
from ....domain.enums.campaign_status import CampaignStatus
from ....domain.enums.enrichment_status import EnrichmentStatus
from ....domain.enums.task_status import TaskStatus
from ....domain.value_objects.campaign import (
    CampaignConfig,
    CampaignGeonameSelectionParams,
    EnrichmentPoolConfig,
)
from ....domain.enums.campaign_scope import CampaignScope
from ....domain.enums.enrichment_type import EnrichmentType
from ....domain.value_objects.geo import Geoname
from ....domain.value_objects.ids import (
    CampaignId,
    EnrichmentTaskId,
    ExtractionTaskId,
    PlaceId,
    ReviewId,
)
from ....domain.value_objects.place import (
    ExtractedPlaceAttributes,
    ExtractedPlaceBookingOption,
    ExtractedPlaceHour,
    ExtractedPlaceHours,
    PlaceEnrichment,
    WebsitePlaceEnrichment,
)
from ..models import (
    CampaignModel,
    ExtractedPlaceModel,
    ExtractedPlaceReviewModel,
    PlaceExtractionTaskModel,
    WebsitePlaceEnrichmentTaskModel,
)


# =============================================================================
# Campaign Mappers
# =============================================================================


def campaign_config_to_dict(config: CampaignConfig) -> dict[str, Any]:
    """Convert CampaignConfig value object to dictionary for JSON storage."""
    return {
        "search_seeds": list(config.search_seeds),
        "geoname_selection_params": {
            "scope": config.geoname_selection_params.scope.value,
            "scope_country_code": config.geoname_selection_params.scope_country_code,
            "scope_geoname_id": config.geoname_selection_params.scope_geoname_id,
            "scope_geoname_name": config.geoname_selection_params.scope_geoname_name,
            "depth_level": config.geoname_selection_params.depth_level.value,
            "min_population": config.geoname_selection_params.min_population,
            "iso_language": config.geoname_selection_params.iso_language,
        },
        "locale": config.locale,
        "max_results": config.max_results,
        "min_rating": config.min_rating,
        "min_num_reviews": config.min_num_reviews,
        "max_reviews": config.max_reviews,
        "max_total_bots": config.max_total_bots,
        "extraction_bots": config.extraction_bots,
        "enrichment_pools": [
            {
                "enrichment_type": pool.enrichment_type.value,
                "bots": pool.bots,
                "enabled": pool.enabled,
            }
            for pool in config.enrichment_pools
        ],
        "max_attempts": config.max_attempts,
    }


def dict_to_campaign_config(data: dict[str, Any]) -> CampaignConfig:
    """Convert dictionary from JSON storage to CampaignConfig value object."""
    gsp = data["geoname_selection_params"]
    return CampaignConfig(
        search_seeds=tuple(data["search_seeds"]),
        geoname_selection_params=CampaignGeonameSelectionParams(
            scope=CampaignScope(gsp["scope"]),
            scope_country_code=gsp.get("scope_country_code"),
            scope_geoname_id=gsp.get("scope_geoname_id"),
            scope_geoname_name=gsp.get("scope_geoname_name"),
            depth_level=CampaignDepthLevel(gsp["depth_level"]),
            min_population=gsp.get("min_population", 15000),
            iso_language=gsp.get("iso_language"),
        ),
        locale=data.get("locale", "en-US"),
        max_results=data.get("max_results", 50),
        min_rating=data.get("min_rating", 4.0),
        min_num_reviews=data.get("min_num_reviews", 0),
        max_reviews=data.get("max_reviews", 0),
        max_total_bots=data.get("max_total_bots", 30),
        extraction_bots=data.get("extraction_bots", 15),
        enrichment_pools=tuple(
            EnrichmentPoolConfig(
                enrichment_type=EnrichmentType(pool["enrichment_type"]),
                bots=pool["bots"],
                enabled=pool.get("enabled", True),
            )
            for pool in data.get("enrichment_pools", [])
        ),
        max_attempts=data.get("max_attempts", 10),
    )


def campaign_to_model(campaign: Campaign) -> CampaignModel:
    """Convert Campaign domain entity to ORM model."""
    return CampaignModel(
        id=campaign.id.value,
        title=campaign.title,
        status=campaign.status.value,
        config=campaign_config_to_dict(campaign.config),
        total_tasks=campaign.total_tasks,
        completed_tasks=campaign.completed_tasks,
        failed_tasks=campaign.failed_tasks,
        created_at=campaign.created_at,
        started_at=campaign.started_at,
        completed_at=campaign.completed_at,
        updated_at=campaign.updated_at,
        tasks=[task_to_model(task) for task in campaign.tasks],
    )


def model_to_campaign(model: CampaignModel) -> Campaign:
    """Convert ORM model to Campaign domain entity."""
    return Campaign(
        id=CampaignId(model.id),
        title=model.title,
        status=CampaignStatus(model.status),
        config=dict_to_campaign_config(model.config),
        total_tasks=model.total_tasks,
        completed_tasks=model.completed_tasks,
        failed_tasks=model.failed_tasks,
        created_at=model.created_at,
        started_at=model.started_at,
        completed_at=model.completed_at,
        updated_at=model.updated_at,
        tasks=[model_to_task(task_model) for task_model in model.tasks],
    )


# =============================================================================
# PlaceExtractionTask Mappers
# =============================================================================


def geoname_to_dict(geoname: Geoname) -> dict[str, Any]:
    """Convert Geoname value object to dictionary for JSON storage."""
    return {
        "name": geoname.name,
        "latitude": geoname.latitude,
        "longitude": geoname.longitude,
        "country_code": geoname.country_code,
        "population": geoname.population,
        "postal_code_regex": geoname.postal_code_regex,
        "country_name": geoname.country_name,
        "admin1_name": geoname.admin1_name,
    }


def dict_to_geoname(data: dict[str, Any]) -> Geoname:
    """Convert dictionary from JSON storage to Geoname value object."""
    return Geoname(
        name=data["name"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        country_code=data["country_code"],
        population=data["population"],
        postal_code_regex=data.get("postal_code_regex"),
        country_name=data.get("country_name"),
        admin1_name=data.get("admin1_name"),
    )


def task_to_model(task: PlaceExtractionTask) -> PlaceExtractionTaskModel:
    """Convert PlaceExtractionTask domain entity to ORM model."""
    return PlaceExtractionTaskModel(
        id=task.id.value,
        campaign_id=task.campaign_id.value,
        search_seed=task.search_seed,
        geoname=geoname_to_dict(task.geoname),
        status=task.status.value,
        attempts=task.attempts,
        last_error=task.last_error,
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        updated_at=task.updated_at,
    )


def model_to_task(model: PlaceExtractionTaskModel) -> PlaceExtractionTask:
    """Convert ORM model to PlaceExtractionTask domain entity."""
    return PlaceExtractionTask(
        id=ExtractionTaskId(model.id),
        campaign_id=CampaignId(model.campaign_id),
        search_seed=model.search_seed,
        geoname=dict_to_geoname(model.geoname),
        status=TaskStatus(model.status),
        attempts=model.attempts,
        last_error=model.last_error,
        created_at=model.created_at,
        started_at=model.started_at,
        completed_at=model.completed_at,
        updated_at=model.updated_at,
    )


# =============================================================================
# ExtractedPlace Mappers
# =============================================================================


def attributes_to_dict(attrs: ExtractedPlaceAttributes | None) -> dict[str, Any] | None:
    """Convert ExtractedPlaceAttributes to dictionary."""
    if attrs is None:
        return None
    return {"attributes": list(attrs.attributes)}


def dict_to_attributes(data: dict[str, Any] | None) -> ExtractedPlaceAttributes | None:
    """Convert dictionary to ExtractedPlaceAttributes."""
    if data is None:
        return None
    return ExtractedPlaceAttributes(attributes=data.get("attributes", []))


def hours_to_dict(hours: ExtractedPlaceHours | None) -> dict[str, Any] | None:
    """Convert ExtractedPlaceHours to dictionary."""
    if hours is None:
        return None
    return {
        "hours": [
            {"day": h.day, "open": h.open, "close": h.close}
            for h in hours.hours
        ]
    }


def dict_to_hours(data: dict[str, Any] | None) -> ExtractedPlaceHours | None:
    """Convert dictionary to ExtractedPlaceHours."""
    if data is None:
        return None
    return ExtractedPlaceHours(
        hours=tuple(
            ExtractedPlaceHour(day=h["day"], open=h["open"], close=h["close"])
            for h in data.get("hours", [])
        )
    )


def booking_option_to_dict(opt: ExtractedPlaceBookingOption) -> dict[str, Any]:
    """Convert ExtractedPlaceBookingOption to dictionary."""
    return {
        "provider_name": opt.provider_name,
        "title": opt.title,
        "provider_logo": opt.provider_logo,
        "image": opt.image,
        "price": opt.price,
        "info_items": list(opt.info_items) if opt.info_items else None,
    }


def dict_to_booking_option(data: dict[str, Any]) -> ExtractedPlaceBookingOption:
    """Convert dictionary to ExtractedPlaceBookingOption."""
    return ExtractedPlaceBookingOption(
        provider_name=data["provider_name"],
        title=data.get("title"),
        provider_logo=data.get("provider_logo"),
        image=data.get("image"),
        price=data.get("price"),
        info_items=tuple(data["info_items"]) if data.get("info_items") else None,
    )


def enrichment_to_dict(enrichment: PlaceEnrichment) -> dict[str, Any]:
    """Convert PlaceEnrichment to dictionary with type discriminator."""
    if isinstance(enrichment, WebsitePlaceEnrichment):
        return {
            "type": "website",
            "extracted_at": enrichment.extracted_at.isoformat(),
            "title": enrichment.title,
            "description": enrichment.description,
            "meta_keywords": list(enrichment.meta_keywords),
            "emails": list(enrichment.emails),
            "social_urls": list(enrichment.social_urls),
        }
    # Add more enrichment types here as needed
    raise ValueError(f"Unknown enrichment type: {type(enrichment)}")


def dict_to_enrichment(data: dict[str, Any]) -> PlaceEnrichment:
    """Convert dictionary to PlaceEnrichment based on type discriminator."""
    from datetime import datetime

    enrichment_type = data.get("type")
    if enrichment_type == "website":
        return WebsitePlaceEnrichment(
            extracted_at=datetime.fromisoformat(data["extracted_at"]),
            title=data.get("title"),
            description=data.get("description"),
            meta_keywords=tuple(data.get("meta_keywords", [])),
            emails=tuple(data.get("emails", [])),
            social_urls=tuple(data.get("social_urls", [])),
        )
    raise ValueError(f"Unknown enrichment type: {enrichment_type}")


def place_to_model(place: ExtractedPlace) -> ExtractedPlaceModel:
    """Convert ExtractedPlace domain entity to ORM model."""
    return ExtractedPlaceModel(
        place_id=place.place_id.value,
        task_id=place.task_id.value if place.task_id else None,
        name=place.name,
        cid=place.cid,
        address=place.address,
        city=place.city,
        state=place.state,
        state_code=place.state_code,
        postal_code=place.postal_code,
        latitude=place.latitude,
        longitude=place.longitude,
        plus_code=place.plus_code,
        rating=place.rating,
        review_count=place.review_count,
        phone=place.phone,
        website_link=place.website_link,
        menu_link=place.menu_link,
        appointment_link=place.appointment_link,
        booking_link=place.booking_link,
        order_online_link=place.order_online_link,
        domain=place.domain,
        category=place.category,
        description=place.description,
        main_image=place.main_image,
        closure_status=place.closure_status,
        claimable=place.claimable,
        average_price=place.average_price,
        attributes=attributes_to_dict(place.attributes),
        hours=hours_to_dict(place.hours),
        booking_options=[booking_option_to_dict(opt) for opt in place.booking_options],
        review_summary=list(place.review_summary),
        enrichment_status=int(place.enrichment_status),
        enrichments=[enrichment_to_dict(e) for e in place.enrichments],
        created_at=place.created_at,
        updated_at=place.updated_at,
        reviews=[review_to_model(r) for r in place.reviews],
    )


def model_to_place(model: ExtractedPlaceModel) -> ExtractedPlace:
    """Convert ORM model to ExtractedPlace domain entity."""
    return ExtractedPlace(
        place_id=PlaceId(model.place_id),
        task_id=ExtractionTaskId(model.task_id) if model.task_id else None,
        name=model.name,
        cid=model.cid,
        address=model.address,
        city=model.city,
        state=model.state,
        state_code=model.state_code,
        postal_code=model.postal_code,
        latitude=model.latitude,
        longitude=model.longitude,
        plus_code=model.plus_code,
        rating=model.rating,
        review_count=model.review_count,
        phone=model.phone,
        website_link=model.website_link,
        menu_link=model.menu_link,
        appointment_link=model.appointment_link,
        booking_link=model.booking_link,
        order_online_link=model.order_online_link,
        domain=model.domain,
        category=model.category,
        description=model.description,
        main_image=model.main_image,
        closure_status=model.closure_status,
        claimable=model.claimable,
        average_price=model.average_price,
        attributes=dict_to_attributes(model.attributes),
        hours=dict_to_hours(model.hours),
        booking_options=[dict_to_booking_option(opt) for opt in model.booking_options],
        review_summary=list(model.review_summary),
        enrichment_status=EnrichmentStatus(model.enrichment_status),
        enrichments=[dict_to_enrichment(e) for e in model.enrichments],
        created_at=model.created_at,
        updated_at=model.updated_at,
        reviews=[model_to_review(r) for r in model.reviews],
    )


# =============================================================================
# ExtractedPlaceReview Mappers
# =============================================================================


def review_to_model(review: ExtractedPlaceReview) -> ExtractedPlaceReviewModel:
    """Convert ExtractedPlaceReview domain entity to ORM model."""
    return ExtractedPlaceReviewModel(
        id=review.id.value,
        place_id=review.place_id.value,
        rating=review.rating,
        author=review.author,
        text=review.text,
        lang=review.lang,
        photos=list(review.photos) if review.photos else None,
        created_at=review.created_at,
    )


def model_to_review(model: ExtractedPlaceReviewModel) -> ExtractedPlaceReview:
    """Convert ORM model to ExtractedPlaceReview domain entity."""
    return ExtractedPlaceReview(
        id=ReviewId(model.id),
        place_id=PlaceId(model.place_id),
        rating=model.rating,
        author=model.author,
        text=model.text,
        lang=model.lang,
        photos=list(model.photos) if model.photos else None,
        created_at=model.created_at,
    )


# =============================================================================
# WebsitePlaceEnrichmentTask Mappers
# =============================================================================


def enrichment_task_to_model(
    task: WebsitePlaceEnrichmentTask,
) -> WebsitePlaceEnrichmentTaskModel:
    """Convert WebsitePlaceEnrichmentTask domain entity to ORM model."""
    return WebsitePlaceEnrichmentTaskModel(
        id=task.id.value,
        place_id=task.place_id.value,
        website_url=task.website_url,
        status=task.status.value,
        attempts=task.attempts,
        last_error=task.last_error,
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        updated_at=task.updated_at,
    )


def model_to_enrichment_task(
    model: WebsitePlaceEnrichmentTaskModel,
) -> WebsitePlaceEnrichmentTask:
    """Convert ORM model to WebsitePlaceEnrichmentTask domain entity."""
    return WebsitePlaceEnrichmentTask(
        id=EnrichmentTaskId(model.id),
        place_id=PlaceId(model.place_id),
        website_url=model.website_url,
        status=TaskStatus(model.status),
        attempts=model.attempts,
        last_error=model.last_error,
        created_at=model.created_at,
        started_at=model.started_at,
        completed_at=model.completed_at,
        updated_at=model.updated_at,
    )
