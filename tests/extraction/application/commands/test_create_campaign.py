"""
Integration tests for CreateCampaignHandler.

Tests the full flow: Command → Handler → GeonameService → DB

Requires the geonames microservice to be running at http://127.0.0.1:8000
"""

import pytest
import requests

from extraction.application.commands.create_campaign import (
    CreateCampaignCommand,
    CreateCampaignHandler,
)
from extraction.application.services import GeonameSelectionService
from extraction.domain.enums.campaign_depth_level import CampaignDepthLevel
from extraction.domain.enums.campaign_status import CampaignStatus
from extraction.domain.enums.task_status import TaskStatus
from extraction.domain.value_objects.campaign import (
    CampaignConfig,
    CampaignGeonameSelectionParams,
)
from extraction.infrastructure.http import HttpGeonameQueryService

GEONAMES_BASE_URL = "http://127.0.0.1:8080"


def is_geonames_service_available() -> bool:
    """Check if the geonames microservice is running."""
    try:
        response = requests.get(f"{GEONAMES_BASE_URL}/countries", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False


# Skip all tests in this module if geonames service is not available
pytestmark = pytest.mark.skipif(
    not is_geonames_service_available(),
    reason="Geonames microservice not available at http://127.0.0.1:8080",
)


@pytest.fixture
def geoname_query_service():
    """Create HttpGeonameQueryService pointing to local microservice."""
    return HttpGeonameQueryService(base_url=GEONAMES_BASE_URL)


@pytest.fixture
def geoname_selection_service(geoname_query_service):
    """Create GeonameSelectionService with real HTTP adapter."""
    return GeonameSelectionService(geoname_query_service)


@pytest.fixture
def handler(uow, geoname_selection_service):
    """Create CreateCampaignHandler with all dependencies."""
    return CreateCampaignHandler(
        uow=uow,
        geoname_service=geoname_selection_service,
    )


class TestCreateCampaignHandler:
    """Integration tests for CreateCampaignHandler."""

    def test_create_campaign_with_spain_admin1(self, handler, uow):
        """
        Test creating a campaign for Spain with ADM1 depth level.

        Should create tasks for each Spanish autonomous community × search seeds.
        """
        # Arrange
        config = CampaignConfig(
            search_seeds=("restaurants",),
            geoname_selection_params=CampaignGeonameSelectionParams(
                scope_country_code="ES",
                min_population=100000,
            ),
        )
        command = CreateCampaignCommand(
            config=config,
            title="Spain Restaurants Campaign",
        )

        # Act
        campaign_id = handler.handle(command)

        # Assert - Campaign was created and persisted
        with uow:
            campaign = uow.campaign_repository.find_by_id(campaign_id)

        assert campaign is not None
        assert campaign.title == "Spain Restaurants Campaign"
        assert campaign.status == CampaignStatus.PENDING
        assert campaign.total_tasks > 0  # Should have tasks for Spanish regions

        # Assert - Tasks were created correctly
        assert len(campaign.tasks) == campaign.total_tasks
        for task in campaign.tasks:
            assert task.status == TaskStatus.PENDING
            assert task.search_seed == "restaurants"
            assert task.geoname.country_code == "ES"

    def test_create_campaign_with_multiple_seeds(self, handler, uow):
        """
        Test creating a campaign with multiple search seeds.

        Should create tasks = geonames × seeds.
        """
        # Arrange
        config = CampaignConfig(
            search_seeds=("hotels", "restaurants", "bars"),
            geoname_selection_params=CampaignGeonameSelectionParams(
                scope_country_code="ES",
                min_population=500000,  # Only large cities
            ),
        )
        command = CreateCampaignCommand(
            config=config,
            title="Spain Hospitality Campaign",
        )

        # Act
        campaign_id = handler.handle(command)

        # Assert
        with uow:
            campaign = uow.campaign_repository.find_by_id(campaign_id)

        assert campaign is not None

        # Count unique geonames
        unique_geonames = {task.geoname.name for task in campaign.tasks}

        # Total tasks should be geonames × 3 seeds
        assert campaign.total_tasks == len(unique_geonames) * 3

        # Each seed should appear for each geoname
        seeds_in_tasks = {task.search_seed for task in campaign.tasks}
        assert seeds_in_tasks == {"hotels", "restaurants", "bars"}

    def test_create_campaign_generates_title_if_not_provided(self, handler, uow):
        """
        Test that a title is auto-generated if not provided.
        """
        # Arrange
        config = CampaignConfig(
            search_seeds=("cafes",),
            geoname_selection_params=CampaignGeonameSelectionParams(
                scope_country_code="IT",
                min_population=1000000,  # Only very large cities
            ),
        )
        command = CreateCampaignCommand(config=config)  # No title

        # Act
        campaign_id = handler.handle(command)

        # Assert
        with uow:
            campaign = uow.campaign_repository.find_by_id(campaign_id)

        assert campaign is not None
        assert campaign.title is not None
        assert len(campaign.title) > 0
        assert "Cafes" in campaign.title  # Should include the seed

    def test_create_campaign_with_no_matching_geonames(self, handler, uow):
        """
        Test creating a campaign with filters that match no geonames.

        Should create a campaign with 0 tasks.
        Note: Uses CITY depth level because min_population filter only works with cities endpoint.
        """
        # Arrange
        config = CampaignConfig(
            search_seeds=("restaurants",),
            geoname_selection_params=CampaignGeonameSelectionParams(
                scope_country_code="ES",
                depth_level=CampaignDepthLevel.CITY,  # Cities endpoint supports min_population
                min_population=999999999,  # Impossibly high
            ),
        )
        command = CreateCampaignCommand(
            config=config,
            title="Empty Campaign",
        )

        # Act
        campaign_id = handler.handle(command)

        # Assert
        with uow:
            campaign = uow.campaign_repository.find_by_id(campaign_id)

        assert campaign is not None
        assert campaign.title == "Empty Campaign"
        assert campaign.total_tasks == 0
        assert len(campaign.tasks) == 0

    def test_create_campaign_persists_config_correctly(self, handler, uow):
        """
        Test that the full CampaignConfig is persisted and retrieved correctly.
        """
        # Arrange
        config = CampaignConfig(
            search_seeds=("spas", "gyms"),
            geoname_selection_params=CampaignGeonameSelectionParams(
                scope_country_code="FR",
                scope_geoname_id=3017382,
                scope_geoname_name="France",
                min_population=200000,
            ),
            locale="fr-FR",
            max_results=75,
            min_rating=4.5,
            max_total_workers=20,
            extraction_workers=10,
        )
        command = CreateCampaignCommand(
            config=config,
            title="France Wellness Campaign",
        )

        # Act
        campaign_id = handler.handle(command)

        # Assert
        with uow:
            campaign = uow.campaign_repository.find_by_id(campaign_id)

        # Verify config was persisted correctly
        assert campaign.config.search_seeds == ("spas", "gyms")
        assert campaign.config.locale == "fr-FR"
        assert campaign.config.max_results == 75
        assert campaign.config.min_rating == 4.5
        assert campaign.config.max_total_workers == 20
        assert campaign.config.extraction_workers == 10

        # Verify geoname selection params
        params = campaign.config.geoname_selection_params
        assert params.scope_country_code == "FR"
        assert params.scope_geoname_id == 3017382
        assert params.scope_geoname_name == "France"
        assert params.min_population == 200000
