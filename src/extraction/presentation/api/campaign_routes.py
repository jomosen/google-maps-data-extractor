"""Campaign routes - HTTP adapter for Campaign operations"""
import os
from fastapi import APIRouter, HTTPException, Depends
from shared.logging import get_logger
from shared.events import EventBus

from extraction.application.commands.create_campaign import (
    CreateCampaignCommand,
    CreateCampaignHandler
)
from extraction.application.services import GeonameSelectionService
from extraction.domain.value_objects.campaign import (
    CampaignConfig,
    CampaignGeonameSelectionParams,
    EnrichmentPoolConfig
)
from extraction.domain.enums import CampaignScope, CampaignDepthLevel, EnrichmentType
from extraction.infrastructure.persistence import create_unit_of_work
from extraction.infrastructure.http import HttpGeonameQueryService
from .dto import CreateCampaignRequest, CampaignResponse

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])
logger = get_logger(__name__)


# Dependency injection
def get_uow():
    """Factory for Unit of Work."""
    return create_unit_of_work("sqlite:///data.db")


def get_geoname_query_service():
    """Factory for Geoname Query Service."""
    base_url = os.getenv("GEONAMES_API_URL", "http://localhost:8080")
    return HttpGeonameQueryService(base_url=base_url)


def get_event_bus():
    """Factory for Event Bus (infrastructure)."""
    return EventBus()


def get_create_campaign_handler(
    uow=Depends(get_uow),
    geoname_query_service=Depends(get_geoname_query_service),
    event_bus=Depends(get_event_bus)
):
    """Factory for CreateCampaignHandler."""
    geoname_selection_service = GeonameSelectionService(geoname_query_service)
    return CreateCampaignHandler(uow, geoname_selection_service, event_bus)


@router.post("", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    request: CreateCampaignRequest,
    handler: CreateCampaignHandler = Depends(get_create_campaign_handler)
) -> CampaignResponse:
    """
    Create a new extraction campaign.
    
    Auto-generates campaign title from activity and geographic scope.
    Persists campaign to database and creates extraction tasks.
    
    Returns:
        CampaignResponse with campaign_id for starting extraction
    """
    try:
        logger.info(
            "create_campaign_request",
            activity=request.activity,
            country=request.country_code
        )
        
        # 1. Build CampaignGeonameSelectionParams
        geoname_params = _build_geoname_params(request)
        
        # 2. Build CampaignConfig
        config = _build_campaign_config(request, geoname_params)
        
        # 3. Generate title automatically
        title = _generate_campaign_title(request)
        
        # 4. Create command
        command = CreateCampaignCommand(
            config=config,
            title=title
        )
        
        # 5. Execute command
        campaign_id = handler.handle(command)
        
        # 6. Load created campaign to build response
        with handler._uow:
            campaign = handler._uow.campaign_repository.get(campaign_id)
        
        logger.info(
            "campaign_created_successfully",
            campaign_id=str(campaign_id),
            title=title,
            total_tasks=campaign.total_tasks
        )
        
        # 7. Build response DTO
        return CampaignResponse(
            campaign_id=str(campaign.id),
            title=campaign.title,
            status=campaign.status.value,
            total_tasks=campaign.total_tasks,
            created_at=campaign.created_at,
            extraction_bots=config.extraction_bots
        )
        
    except ValueError as e:
        logger.error("create_campaign_validation_error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "create_campaign_error",
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail="Failed to create campaign")


def _build_geoname_params(request: CreateCampaignRequest) -> CampaignGeonameSelectionParams:
    """
    Build CampaignGeonameSelectionParams from request.
    
    Uses explicit scope data from frontend (scope, scope_geoname_id, scope_geoname_name).
    Falls back to legacy inferring from region/province/city fields if scope not provided.
    """
    # Use explicit scope if provided (new approach)
    if request.scope:
        scope_map = {
            "country": CampaignScope.COUNTRY,
            "admin1": CampaignScope.ADMIN1,
            "admin2": CampaignScope.ADMIN2,
            "city": CampaignScope.CITY
        }
        scope = scope_map.get(request.scope, CampaignScope.COUNTRY)
        scope_geoname_id = request.scope_geoname_id
        scope_geoname_name = request.scope_geoname_name
    else:
        # Legacy: infer from region/province/city fields
        if request.city:
            scope = CampaignScope.CITY
            scope_geoname_name = request.city
            scope_geoname_id = None  # Not available in legacy mode
        elif request.province:
            scope = CampaignScope.ADMIN2
            scope_geoname_name = request.province
            scope_geoname_id = None
        elif request.region:
            scope = CampaignScope.ADMIN1
            scope_geoname_name = request.region
            scope_geoname_id = None
        else:
            scope = CampaignScope.COUNTRY
            scope_geoname_name = None
            scope_geoname_id = None
    
    return CampaignGeonameSelectionParams(
        scope=scope,
        scope_country_code=request.country_code,
        scope_geoname_id=scope_geoname_id,
        scope_geoname_name=scope_geoname_name,
        min_population=request.min_population or 15000,
        iso_language=request.locale.split('-')[0] if request.locale else "en"
    )


def _build_campaign_config(
    request: CreateCampaignRequest,
    geoname_params: CampaignGeonameSelectionParams
) -> CampaignConfig:
    """
    Build CampaignConfig from request.
    
    Uses domain defaults for bot allocation:
    - max_total_bots: 30
    - extraction_bots: 15
    - enrichment bots: 15 (website enrichment)
    """
    # Use domain defaults (defined in CampaignConfig)
    extraction_bots = 15
    max_total_bots = 30
    enrichment_bots = max_total_bots - extraction_bots
    
    return CampaignConfig(
        search_seeds=(request.activity,),  # Single activity for now
        geoname_selection_params=geoname_params,
        locale=request.locale or "en-US",
        max_results=request.max_results or 50,
        min_rating=request.min_rating or 4.0,
        min_num_reviews=0,
        max_reviews=0,
        max_total_bots=max_total_bots,
        extraction_bots=extraction_bots,
        enrichment_pools=(
            EnrichmentPoolConfig(
                enrichment_type=EnrichmentType.WEBSITE,
                bots=enrichment_bots,
                enabled=True
            ),
        ),
        max_attempts=10
    )


def _generate_campaign_title(request: CreateCampaignRequest) -> str:
    """
    Generate campaign title automatically from activity and geography.
    
    Format: "{Activity} in {Location}"
    
    Examples:
        - "Restaurants in Madrid, Spain"
        - "Hotels in Barcelona, Catalonia, Spain"
        - "Cafes in Valencia, Spain"
    """
    activity = request.activity.capitalize()
    
    # Build location string (most specific to least specific)
    location_parts = []
    if request.city:
        location_parts.append(request.city)
    if request.province and request.province != request.city:
        location_parts.append(request.province)
    if request.region and request.region not in location_parts:
        location_parts.append(request.region)
    
    # Always include country code at the end
    location_parts.append(request.country_code)
    
    location = ", ".join(location_parts)
    
    return f"{activity} in {location}"


@router.get("", response_model=list[CampaignResponse])
async def list_campaigns():
    """
    List all campaigns.
    
    TODO: Implement pagination and filtering.
    """
    # TODO: Implement GetCampaignsQuery (CQRS read side)
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: str):
    """
    Get campaign by ID.
    
    TODO: Implement GetCampaignQuery (CQRS read side).
    """
    # TODO: Implement GetCampaignQuery
    raise HTTPException(status_code=501, detail="Not implemented yet")
