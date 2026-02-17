from __future__ import annotations

from typing import Optional

from sqlalchemy import update
from sqlalchemy.orm import Session

from ....domain.entities.campaign import Campaign
from ....domain.interfaces.campaign_repository import CampaignRepository
from ....domain.value_objects.ids import CampaignId
from ..models import CampaignModel, PlaceExtractionTaskModel
from .mappers import campaign_to_model, model_to_campaign, task_to_model


class SqlAlchemyCampaignRepository(CampaignRepository):
    """
    SQLAlchemy implementation of CampaignRepository.

    Handles persistence of Campaign aggregate including child tasks.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, campaign: Campaign) -> None:
        """
        Persiste el agregado Campaign (insert o update).

        Incluye todas las entidades hijas (tasks).
        """
        existing = self._session.get(CampaignModel, campaign.id.value)

        if existing is None:
            # Insert new campaign with tasks
            model = campaign_to_model(campaign)
            self._session.add(model)
        else:
            # Update existing campaign
            existing.title = campaign.title
            existing.status = campaign.status.value
            existing.config = campaign_to_model(campaign).config
            existing.total_tasks = campaign.total_tasks
            existing.completed_tasks = campaign.completed_tasks
            existing.failed_tasks = campaign.failed_tasks
            existing.started_at = campaign.started_at
            existing.completed_at = campaign.completed_at
            existing.updated_at = campaign.updated_at

            # Sync tasks: delete removed, update existing, add new
            existing_task_ids = {t.id for t in existing.tasks}
            new_task_ids = {t.id.value for t in campaign.tasks}

            # Delete tasks that are no longer in the campaign
            for task_model in list(existing.tasks):
                if task_model.id not in new_task_ids:
                    self._session.delete(task_model)

            # Add or update tasks
            for task in campaign.tasks:
                if task.id.value in existing_task_ids:
                    # Update existing task
                    task_model = next(
                        t for t in existing.tasks if t.id == task.id.value
                    )
                    task_model.status = task.status.value
                    task_model.attempts = task.attempts
                    task_model.last_error = task.last_error
                    task_model.started_at = task.started_at
                    task_model.completed_at = task.completed_at
                    task_model.updated_at = task.updated_at
                else:
                    # Add new task
                    new_task_model = task_to_model(task)
                    existing.tasks.append(new_task_model)

    def find_by_id(self, campaign_id: CampaignId) -> Optional[Campaign]:
        """
        Carga el agregado Campaign para modificacion.
        """
        model = self._session.get(CampaignModel, campaign_id.value)
        if model is None:
            return None
        return model_to_campaign(model)

    def delete(self, campaign_id: CampaignId) -> None:
        """
        Elimina el agregado y todas sus entidades hijas (cascade).
        """
        model = self._session.get(CampaignModel, campaign_id.value)
        if model is not None:
            self._session.delete(model)

    def increment_completed(self, campaign_id: CampaignId) -> None:
        """
        Incrementa atomicamente el contador de tareas completadas.
        """
        stmt = (
            update(CampaignModel)
            .where(CampaignModel.id == campaign_id.value)
            .values(completed_tasks=CampaignModel.completed_tasks + 1)
        )
        self._session.execute(stmt)

    def increment_failed(self, campaign_id: CampaignId) -> None:
        """
        Incrementa atomicamente el contador de tareas fallidas.
        """
        stmt = (
            update(CampaignModel)
            .where(CampaignModel.id == campaign_id.value)
            .values(failed_tasks=CampaignModel.failed_tasks + 1)
        )
        self._session.execute(stmt)
