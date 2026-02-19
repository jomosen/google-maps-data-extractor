"""Command handler for archiving a campaign."""

from __future__ import annotations

from dataclasses import dataclass

from ...domain.interfaces.unit_of_work import AbstractUnitOfWork
from ...domain.value_objects.ids import CampaignId


@dataclass(frozen=True)
class ArchiveCampaignCommand:
    campaign_id: CampaignId


class ArchiveCampaignHandler:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    def handle(self, command: ArchiveCampaignCommand) -> None:
        with self._uow:
            campaign = self._uow.campaign_repository.find_by_id(command.campaign_id)

            if campaign is None:
                raise ValueError(f"Campaign {command.campaign_id} not found.")

            campaign.mark_archived()

            self._uow.campaign_repository.save(campaign)
            self._uow.commit()
