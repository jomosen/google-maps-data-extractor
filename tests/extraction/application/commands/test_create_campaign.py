"""
Integration tests for CreateCampaignHandler.

Tests the full flow: Command → Handler → GeonameService → DB

Requires the geonames microservice to be running at http://127.0.0.1:8080
"""

import pytest
import requests

from extraction.application.commands.create_campaign import (
    CreateCampaignCommand,
    CreateCampaignHandler,
)
from extraction.domain.services import GeonameSelectionService
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

    def test_create_campaign_country_scope(self, handler, uow):
        """
        Test creating a campaign scoped to a full country.

        Should create tasks for all cities in Spain above min_population.
        """
        config = CampaignConfig(
            search_seeds=("restaurants",),
            geoname_selection_params=CampaignGeonameSelectionParams(
                country_code="ES",
                min_population=100000,
                location_name="Spain",
            ),
        )
        command = CreateCampaignCommand(
            config=config,
            title="Spain Restaurants Campaign",
        )

        campaign_id = handler.handle(command)

        with uow:
            campaign = uow.campaign_repository.find_by_id(campaign_id)

        assert campaign is not None
        assert campaign.title == "Spain Restaurants Campaign"
        assert campaign.status == CampaignStatus.PENDING
        assert campaign.total_tasks > 0

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
        config = CampaignConfig(
            search_seeds=("hotels", "restaurants", "bars"),
            geoname_selection_params=CampaignGeonameSelectionParams(
                country_code="ES",
                min_population=500000,
                location_name="Spain",
            ),
        )
        command = CreateCampaignCommand(
            config=config,
            title="Spain Hospitality Campaign",
        )

        campaign_id = handler.handle(command)

        with uow:
            campaign = uow.campaign_repository.find_by_id(campaign_id)

        assert campaign is not None

        unique_geonames = {task.geoname.name for task in campaign.tasks}
        assert campaign.total_tasks == len(unique_geonames) * 3

        seeds_in_tasks = {task.search_seed for task in campaign.tasks}
        assert seeds_in_tasks == {"hotels", "restaurants", "bars"}

    def test_create_campaign_admin1_scope(self, handler, uow):
        """
        Test creating a campaign scoped to a single admin1 region.

        Should create tasks only for cities within that region.
        """
        config = CampaignConfig(
            search_seeds=("cafes",),
            geoname_selection_params=CampaignGeonameSelectionParams(
                country_code="ES",
                admin1_code="MD",  # Comunidad de Madrid
                min_population=50000,
                location_name="Comunidad de Madrid, ES",
            ),
        )
        command = CreateCampaignCommand(
            config=config,
            title="Madrid Region Cafes Campaign",
        )

        campaign_id = handler.handle(command)

        with uow:
            campaign = uow.campaign_repository.find_by_id(campaign_id)

        assert campaign is not None
        assert campaign.total_tasks > 0

    def test_create_campaign_with_no_matching_geonames(self, handler, uow):
        """
        Test creating a campaign with a min_population that matches no cities.

        Should create a campaign with 0 tasks.
        """
        config = CampaignConfig(
            search_seeds=("restaurants",),
            geoname_selection_params=CampaignGeonameSelectionParams(
                country_code="ES",
                min_population=999999999,  # Impossibly high
                location_name="Spain",
            ),
        )
        command = CreateCampaignCommand(
            config=config,
            title="Empty Campaign",
        )

        campaign_id = handler.handle(command)

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
        config = CampaignConfig(
            search_seeds=("spas", "gyms"),
            geoname_selection_params=CampaignGeonameSelectionParams(
                country_code="FR",
                admin1_code="A8",  # Île-de-France
                min_population=200000,
                iso_language="fr",
                location_name="Île-de-France, FR",
            ),
            locale="fr-FR",
            max_results=75,
            min_rating=4.5,
            max_bots=20,
        )
        command = CreateCampaignCommand(
            config=config,
            title="France Wellness Campaign",
        )

        campaign_id = handler.handle(command)

        with uow:
            campaign = uow.campaign_repository.find_by_id(campaign_id)

        assert campaign.config.search_seeds == ("spas", "gyms")
        assert campaign.config.locale == "fr-FR"
        assert campaign.config.max_results == 75
        assert campaign.config.min_rating == 4.5
        assert campaign.config.max_bots == 20

        params = campaign.config.geoname_selection_params
        assert params.country_code == "FR"
        assert params.admin1_code == "A8"
        assert params.min_population == 200000
        assert params.iso_language == "fr"
        assert params.location_name == "Île-de-France, FR"
