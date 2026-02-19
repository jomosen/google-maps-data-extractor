"""Campaign routes - HTTP adapter for Campaign operations."""
import os
import pathlib

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from shared.events import EventBus
from shared.logging import get_logger

from extraction.application.commands.create_campaign import (
    CreateCampaignCommand,
    CreateCampaignHandler,
)
from extraction.application.commands.start_campaign import (
    StartCampaignCommand,
    StartCampaignHandler,
)
from extraction.application.commands.resume_campaign import (
    ResumeCampaignCommand,
    ResumeCampaignHandler,
)
from extraction.application.commands.archive_campaign import (
    ArchiveCampaignCommand,
    ArchiveCampaignHandler,
)
from extraction.application.queries.get_campaigns import GetCampaignsQuery, GetCampaignsHandler
from extraction.application.queries.get_campaign_by_id import GetCampaignByIdQuery, GetCampaignByIdHandler
from extraction.application.queries.get_campaign_places import GetCampaignPlacesQuery, GetCampaignPlacesHandler
from extraction.application.queries.get_campaign_tasks import GetCampaignTasksQuery, GetCampaignTasksHandler
from extraction.domain.services import GeonameSelectionService
from extraction.domain.value_objects.campaign import (
    CampaignConfig,
    CampaignGeonameSelectionParams,
    EnrichmentPoolConfig,
)
from extraction.domain.value_objects.ids import CampaignId
from extraction.domain.enums import EnrichmentType
from extraction.infrastructure.http import HttpGeonameQueryService
from extraction.infrastructure.persistence import create_unit_of_work
from extraction.infrastructure.persistence.repositories import (
    SqlAlchemyCampaignQueryRepository,
    SqlAlchemyPlaceQueryRepository,
    SqlAlchemyTaskQueryRepository,
)
from .dto import CampaignResponse, CampaignDetailResponse, PlaceResponse, TaskResponse, CreateCampaignRequest

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])
logger = get_logger(__name__)

# api/ → presentation/ → extraction/ → src/ → root
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_PROJECT_ROOT / 'data.db'}")


# ---------------------------------------------------------------------------
# Dependency factories
# ---------------------------------------------------------------------------

def get_uow():
    return create_unit_of_work(DATABASE_URL)


def get_geoname_query_service():
    base_url = os.getenv("GEONAMES_API_URL", "http://localhost:8080")
    return HttpGeonameQueryService(base_url=base_url)


def get_event_bus():
    return EventBus()


def get_db_session():
    engine = create_engine(DATABASE_URL)
    session: Session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


def get_create_campaign_handler(
    uow=Depends(get_uow),
    geoname_query_service=Depends(get_geoname_query_service),
    event_bus=Depends(get_event_bus),
):
    geoname_selection_service = GeonameSelectionService(geoname_query_service)
    return CreateCampaignHandler(uow, geoname_selection_service, event_bus)


def get_campaigns_handler(session: Session = Depends(get_db_session)):
    return GetCampaignsHandler(SqlAlchemyCampaignQueryRepository(session))


def get_campaign_by_id_handler(session: Session = Depends(get_db_session)):
    return GetCampaignByIdHandler(SqlAlchemyCampaignQueryRepository(session))


def get_campaign_places_handler(session: Session = Depends(get_db_session)):
    return GetCampaignPlacesHandler(SqlAlchemyPlaceQueryRepository(session))


def get_campaign_tasks_handler(session: Session = Depends(get_db_session)):
    return GetCampaignTasksHandler(SqlAlchemyTaskQueryRepository(session))


def get_start_handler(uow=Depends(get_uow)):
    return StartCampaignHandler(uow)


def get_resume_handler(uow=Depends(get_uow)):
    return ResumeCampaignHandler(uow)


def get_archive_handler(uow=Depends(get_uow)):
    return ArchiveCampaignHandler(uow)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=list[CampaignResponse])
async def list_campaigns(
    handler: GetCampaignsHandler = Depends(get_campaigns_handler),
) -> list[CampaignResponse]:
    """List all campaigns ordered by creation date descending."""
    try:
        dtos = handler.handle(GetCampaignsQuery())
        return [
            CampaignResponse(
                campaign_id=dto.campaign_id,
                title=dto.title,
                status=dto.status,
                total_tasks=dto.total_tasks,
                created_at=dto.created_at,
                max_bots=dto.max_bots,
                activity=dto.activity,
                location_name=dto.location_name,
            )
            for dto in dtos
        ]
    except Exception as e:
        logger.error("list_campaigns_error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve campaigns")


@router.post("", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    request: CreateCampaignRequest,
    handler: CreateCampaignHandler = Depends(get_create_campaign_handler),
) -> CampaignResponse:
    """
    Create a new extraction campaign.

    Derives geographic scope from whichever admin fields are populated.
    Title is auto-generated from activity and location_name.
    """
    try:
        logger.info(
            "create_campaign_request",
            activity=request.activity,
            country=request.country_code,
        )

        geoname_params = _build_geoname_params(request)
        config = _build_campaign_config(request, geoname_params)
        title = f"{request.activity.capitalize()} in {request.location_name or request.country_code}"

        campaign_id = handler.handle(CreateCampaignCommand(config=config, title=title))

        with handler._uow:
            campaign = handler._uow.campaign_repository.find_by_id(campaign_id)

        logger.info(
            "campaign_created_successfully",
            campaign_id=str(campaign_id),
            title=title,
            total_tasks=campaign.total_tasks,
        )

        return CampaignResponse(
            campaign_id=str(campaign.id),
            title=campaign.title,
            status=campaign.status.value,
            total_tasks=campaign.total_tasks,
            created_at=campaign.created_at,
            max_bots=config.max_bots,
            activity=request.activity,
            location_name=request.location_name or "",
        )

    except ValueError as e:
        logger.error("create_campaign_validation_error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("create_campaign_error", error=str(e), error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to create campaign")


@router.get("/{campaign_id}", response_model=CampaignDetailResponse)
async def get_campaign(
    campaign_id: str,
    handler: GetCampaignByIdHandler = Depends(get_campaign_by_id_handler),
) -> CampaignDetailResponse:
    """Get campaign detail by ID."""
    try:
        dto = handler.handle(GetCampaignByIdQuery(campaign_id=campaign_id))
        if dto is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return CampaignDetailResponse(
            campaign_id=dto.campaign_id,
            title=dto.title,
            status=dto.status,
            total_tasks=dto.total_tasks,
            completed_tasks=dto.completed_tasks,
            failed_tasks=dto.failed_tasks,
            completion_percentage=dto.completion_percentage,
            created_at=dto.created_at,
            started_at=dto.started_at,
            completed_at=dto.completed_at,
            max_bots=dto.max_bots,
            activity=dto.activity,
            location_name=dto.location_name,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_campaign_error", campaign_id=campaign_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve campaign")


@router.get("/{campaign_id}/places", response_model=list[PlaceResponse])
async def get_campaign_places(
    campaign_id: str,
    handler: GetCampaignPlacesHandler = Depends(get_campaign_places_handler),
) -> list[PlaceResponse]:
    """Get all extracted places for a campaign."""
    try:
        dtos = handler.handle(GetCampaignPlacesQuery(campaign_id=campaign_id))
        return [
            PlaceResponse(
                place_id=dto.place_id,
                name=dto.name,
                address=dto.address,
                city=dto.city,
                rating=dto.rating,
                review_count=dto.review_count,
                phone=dto.phone,
                website_link=dto.website_link,
                category=dto.category,
            )
            for dto in dtos
        ]
    except Exception as e:
        logger.error("get_campaign_places_error", campaign_id=campaign_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve places")


@router.get("/{campaign_id}/tasks", response_model=list[TaskResponse])
async def get_campaign_tasks(
    campaign_id: str,
    handler: GetCampaignTasksHandler = Depends(get_campaign_tasks_handler),
) -> list[TaskResponse]:
    """Get all extraction tasks for a campaign."""
    try:
        dtos = handler.handle(GetCampaignTasksQuery(campaign_id=campaign_id))
        return [
            TaskResponse(
                task_id=dto.task_id,
                search_seed=dto.search_seed,
                geoname_name=dto.geoname_name,
                status=dto.status,
                attempts=dto.attempts,
                last_error=dto.last_error,
                created_at=dto.created_at,
            )
            for dto in dtos
        ]
    except Exception as e:
        logger.error("get_campaign_tasks_error", campaign_id=campaign_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve tasks")


@router.post("/{campaign_id}/start", status_code=204)
async def start_campaign(
    campaign_id: str,
    handler: StartCampaignHandler = Depends(get_start_handler),
) -> None:
    """Start a PENDING campaign."""
    try:
        handler.handle(StartCampaignCommand(campaign_id=CampaignId(campaign_id)))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("start_campaign_error", campaign_id=campaign_id, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{campaign_id}/resume", status_code=204)
async def resume_campaign(
    campaign_id: str,
    handler: ResumeCampaignHandler = Depends(get_resume_handler),
) -> None:
    """Resume a FAILED campaign."""
    try:
        handler.handle(ResumeCampaignCommand(campaign_id=CampaignId(campaign_id)))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("resume_campaign_error", campaign_id=campaign_id, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{campaign_id}/archive", status_code=204)
async def archive_campaign(
    campaign_id: str,
    handler: ArchiveCampaignHandler = Depends(get_archive_handler),
) -> None:
    """Archive a COMPLETED or FAILED campaign."""
    try:
        handler.handle(ArchiveCampaignCommand(campaign_id=CampaignId(campaign_id)))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("archive_campaign_error", campaign_id=campaign_id, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_geoname_params(request: CreateCampaignRequest) -> CampaignGeonameSelectionParams:
    """Map request fields directly onto CampaignGeonameSelectionParams."""
    return CampaignGeonameSelectionParams(
        country_code=request.country_code,
        admin1_code=request.admin1_code,
        admin2_code=request.admin2_code,
        city_geoname_id=request.city_geoname_id,
        iso_language=request.iso_language,
        location_name=request.location_name,
    )


def _build_campaign_config(
    request: CreateCampaignRequest,
    geoname_params: CampaignGeonameSelectionParams,
) -> CampaignConfig:
    locale = (
        f"{request.iso_language}-{request.country_code}"
        if request.iso_language
        else "en-US"
    )
    return CampaignConfig(
        search_seeds=(request.activity,),
        geoname_selection_params=geoname_params,
        locale=locale,
        min_num_reviews=0,
        max_reviews=0,
        max_bots=30,
        enrichment_pools=(
            EnrichmentPoolConfig(
                enrichment_type=EnrichmentType.WEBSITE,
                bots=30,
                enabled=True,
            ),
        ),
        max_attempts=10,
    )
