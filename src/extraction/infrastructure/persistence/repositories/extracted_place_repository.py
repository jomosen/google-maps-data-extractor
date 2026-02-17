from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ....domain.entities.extracted_place import ExtractedPlace
from ....domain.interfaces.extracted_place_repository import ExtractedPlaceRepository
from ....domain.value_objects.ids import PlaceId
from ..models import ExtractedPlaceModel
from .mappers import model_to_place, place_to_model, review_to_model


class SqlAlchemyExtractedPlaceRepository(ExtractedPlaceRepository):
    """
    SQLAlchemy implementation of ExtractedPlaceRepository.

    Handles persistence of ExtractedPlace aggregate including child reviews.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, place: ExtractedPlace) -> None:
        """
        Persiste el agregado ExtractedPlace con todas sus entidades hijas.

        Incluye:
        - Reviews
        - Booking options (as JSON)
        - Enrichments (as JSON)
        """
        existing = self._session.get(ExtractedPlaceModel, place.place_id.value)

        if existing is None:
            # Insert new place with reviews
            model = place_to_model(place)
            self._session.add(model)
        else:
            # Update existing place
            existing.task_id = place.task_id.value if place.task_id else None
            existing.name = place.name
            existing.cid = place.cid
            existing.address = place.address
            existing.city = place.city
            existing.state = place.state
            existing.state_code = place.state_code
            existing.postal_code = place.postal_code
            existing.latitude = place.latitude
            existing.longitude = place.longitude
            existing.plus_code = place.plus_code
            existing.rating = place.rating
            existing.review_count = place.review_count
            existing.phone = place.phone
            existing.website_link = place.website_link
            existing.menu_link = place.menu_link
            existing.appointment_link = place.appointment_link
            existing.booking_link = place.booking_link
            existing.order_online_link = place.order_online_link
            existing.domain = place.domain
            existing.category = place.category
            existing.description = place.description
            existing.main_image = place.main_image
            existing.closure_status = place.closure_status
            existing.claimable = place.claimable
            existing.average_price = place.average_price
            existing.updated_at = place.updated_at
            existing.enrichment_status = int(place.enrichment_status)

            # Update JSON fields
            new_model = place_to_model(place)
            existing.attributes = new_model.attributes
            existing.hours = new_model.hours
            existing.booking_options = new_model.booking_options
            existing.review_summary = new_model.review_summary
            existing.enrichments = new_model.enrichments

            # Sync reviews
            existing_review_ids = {r.id for r in existing.reviews}
            new_review_ids = {r.id.value for r in place.reviews}

            # Delete reviews that are no longer in the place
            for review_model in list(existing.reviews):
                if review_model.id not in new_review_ids:
                    self._session.delete(review_model)

            # Add new reviews (reviews are typically immutable)
            for review in place.reviews:
                if review.id.value not in existing_review_ids:
                    new_review_model = review_to_model(review)
                    existing.reviews.append(new_review_model)

    def find_by_place_id(self, place_id: PlaceId) -> Optional[ExtractedPlace]:
        """
        Carga el agregado para modificacion/enriquecimiento.
        """
        model = self._session.get(ExtractedPlaceModel, place_id.value)
        if model is None:
            return None
        return model_to_place(model)

    def exists_by_place_id(self, place_id: PlaceId) -> bool:
        """
        Verifica si existe un place con el ID dado.

        Mas eficiente que find_by_place_id cuando solo se necesita
        verificar existencia.
        """
        stmt = select(ExtractedPlaceModel.place_id).where(
            ExtractedPlaceModel.place_id == place_id.value
        )
        result = self._session.execute(stmt).first()
        return result is not None
