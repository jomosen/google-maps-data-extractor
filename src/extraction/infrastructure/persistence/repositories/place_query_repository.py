"""SQLAlchemy implementation of the PlaceQueryRepository read port."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ....domain.interfaces.place_query_repository import PlaceQueryRepository
from ....application.queries.dtos.place_dto import PlaceDto
from ..models.extracted_place_model import ExtractedPlaceModel
from ..models.place_extraction_task_model import PlaceExtractionTaskModel


class SqlAlchemyPlaceQueryRepository(PlaceQueryRepository):
    """Read-side adapter for PlaceQueryRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_campaign(self, campaign_id: str) -> list[PlaceDto]:
        stmt = (
            select(ExtractedPlaceModel)
            .join(
                PlaceExtractionTaskModel,
                ExtractedPlaceModel.task_id == PlaceExtractionTaskModel.id,
            )
            .where(PlaceExtractionTaskModel.campaign_id == campaign_id)
            .order_by(ExtractedPlaceModel.name)
        )
        models = self._session.scalars(stmt).all()
        return [self._to_dto(m) for m in models]

    @staticmethod
    def _to_dto(model: ExtractedPlaceModel) -> PlaceDto:
        return PlaceDto(
            place_id=model.place_id,
            name=model.name,
            address=model.address,
            city=model.city,
            rating=model.rating,
            review_count=model.review_count,
            phone=model.phone,
            website_link=model.website_link,
            category=model.category,
        )
