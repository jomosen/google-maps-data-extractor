"""SQLAlchemy implementation of the TaskQueryRepository read port."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ....domain.interfaces.task_query_repository import TaskQueryRepository
from ....application.queries.dtos.task_dto import TaskDto
from ..models.place_extraction_task_model import PlaceExtractionTaskModel


class SqlAlchemyTaskQueryRepository(TaskQueryRepository):
    """Read-side adapter for TaskQueryRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_campaign(self, campaign_id: str) -> list[TaskDto]:
        stmt = (
            select(PlaceExtractionTaskModel)
            .where(PlaceExtractionTaskModel.campaign_id == campaign_id)
            .order_by(PlaceExtractionTaskModel.created_at)
        )
        models = self._session.scalars(stmt).all()
        return [self._to_dto(m) for m in models]

    @staticmethod
    def _to_dto(model: PlaceExtractionTaskModel) -> TaskDto:
        geoname = model.geoname or {}
        return TaskDto(
            task_id=model.id,
            search_seed=model.search_seed,
            geoname_name=geoname.get("name", ""),
            status=model.status,
            attempts=model.attempts,
            last_error=model.last_error,
            created_at=model.created_at,
        )
