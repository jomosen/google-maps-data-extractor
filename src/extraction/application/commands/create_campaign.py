from __future__ import annotations

from dataclasses import dataclass

from ...domain.entities.campaign import Campaign
from ...domain.entities.place_extraction_task import PlaceExtractionTask
from ...domain.interfaces.unit_of_work import AbstractUnitOfWork
from ...domain.value_objects.campaign import CampaignConfig
from ...domain.value_objects.geo import Geoname
from ...domain.value_objects.ids import CampaignId
from shared.logging import get_logger
from shared.events import EventBus
from ...domain.services import GeonameSelectionService

logger = get_logger(__name__)


@dataclass(frozen=True)
class CreateCampaignCommand:
    config: CampaignConfig
    title: str | None = None


class CreateCampaignHandler:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        geoname_service: GeonameSelectionService,
        event_bus: EventBus,
    ) -> None:
        self._uow = uow
        self._geoname_service = geoname_service
        self._event_bus = event_bus

    def handle(self, command: CreateCampaignCommand) -> CampaignId:
        campaign = Campaign.create(
            title=command.title,
            config=command.config,
        )

        geonames = self._geoname_service.select(
            command.config.geoname_selection_params
        )

        tasks = self._build_tasks(campaign.id, command.config, geonames)
        campaign.add_tasks(tasks)

        with self._uow:
            self._uow.campaign_repository.save(campaign)
            self._uow.commit()

        logger.info(
            "campaign_created",
            campaign_id=str(campaign.id),
            title=campaign.title,
            total_tasks=campaign.total_tasks,
        )

        return campaign.id

    def _build_tasks(
        self,
        campaign_id: CampaignId,
        config: CampaignConfig,
        geonames: list[Geoname],
    ) -> list[PlaceExtractionTask]:
        return [
            PlaceExtractionTask.create(
                campaign_id=campaign_id,
                event_bus=self._event_bus,
                search_seed=seed,
                geoname=geoname,
            )
            for geoname in geonames
            for seed in config.search_seeds
        ]
