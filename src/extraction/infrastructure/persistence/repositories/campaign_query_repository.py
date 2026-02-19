"""SQLAlchemy implementation of the CampaignQueryRepository read port."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ....domain.interfaces.campaign_query_repository import CampaignQueryRepository
from ....application.queries.dtos.campaign_dto import CampaignDto
from ..models import CampaignModel


class SqlAlchemyCampaignQueryRepository(CampaignQueryRepository):
    """
    Read-side adapter for CampaignQueryRepository.

    Queries CampaignModel directly without reconstructing full Campaign aggregates.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def find_all(self) -> list[CampaignDto]:
        stmt = select(CampaignModel).order_by(CampaignModel.created_at.desc())
        models = self._session.scalars(stmt).all()
        return [self._to_dto(m) for m in models]

    def find_by_id(self, campaign_id: str) -> CampaignDto | None:
        model = self._session.get(CampaignModel, campaign_id)
        if model is None:
            return None
        return self._to_dto(model)

    @staticmethod
    def _to_dto(model: CampaignModel) -> CampaignDto:
        config = model.config
        search_seeds = config.get("search_seeds", [])
        return CampaignDto(
            campaign_id=model.id,
            title=model.title,
            status=model.status,
            total_tasks=model.total_tasks,
            completed_tasks=model.completed_tasks,
            failed_tasks=model.failed_tasks,
            created_at=model.created_at,
            started_at=model.started_at,
            completed_at=model.completed_at,
            max_bots=config.get("max_bots", 0),
            activity=search_seeds[0] if search_seeds else "",
            location_name=config.get("geoname_selection_params", {}).get(
                "location_name", ""
            ),
        )
