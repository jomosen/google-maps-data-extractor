"""
Integration tests for Campaign persistence.

Tests the full flow: Domain Entity → ORM Model → Database → ORM Model → Domain Entity
"""

import pytest

from extraction.domain.entities.campaign import Campaign
from extraction.domain.entities.place_extraction_task import PlaceExtractionTask
from extraction.domain.enums.campaign_status import CampaignStatus
from extraction.domain.enums.task_status import TaskStatus
from extraction.domain.value_objects.campaign import (
    CampaignConfig,
    CampaignGeonameSelectionParams,
)
from extraction.domain.value_objects.geo import Geoname
from extraction.domain.value_objects.ids import CampaignId


@pytest.fixture
def sample_config():
    """Create a sample CampaignConfig for testing."""
    return CampaignConfig(
        search_seeds=("restaurants", "hotels"),
        geoname_selection_params=CampaignGeonameSelectionParams(
            scope_country_code="ES",
            scope_geoname_id=2510769,
            scope_geoname_name="Spain",
            min_population=50000,
        ),
        max_results=100,
        min_rating=4.0,
    )


@pytest.fixture
def sample_geonames():
    """Create sample Geoname objects for testing."""
    return [
        Geoname(
            name="Madrid",
            latitude=40.4168,
            longitude=-3.7038,
            country_code="ES",
            population=3223334,
            country_name="Spain",
            admin1_name="Community of Madrid",
        ),
        Geoname(
            name="Barcelona",
            latitude=41.3851,
            longitude=2.1734,
            country_code="ES",
            population=1620343,
            country_name="Spain",
            admin1_name="Catalonia",
        ),
    ]


class TestCampaignRepository:
    """Integration tests for SqlAlchemyCampaignRepository."""

    def test_save_and_retrieve_campaign_without_tasks(self, uow, sample_config):
        """Test saving and retrieving a Campaign without tasks."""
        # Arrange
        campaign = Campaign.create(title="Test Campaign", config=sample_config)

        # Act - Save
        with uow:
            uow.campaign_repository.save(campaign)
            uow.commit()

        # Act - Retrieve
        with uow:
            retrieved = uow.campaign_repository.find_by_id(campaign.id)

        # Assert
        assert retrieved is not None
        assert retrieved.id == campaign.id
        assert retrieved.title == "Test Campaign"
        assert retrieved.status == CampaignStatus.PENDING
        assert retrieved.config.search_seeds == ("restaurants", "hotels")
        assert retrieved.config.geoname_selection_params.scope_country_code == "ES"
        assert retrieved.total_tasks == 0
        assert retrieved.tasks == []

    def test_save_and_retrieve_campaign_with_tasks(
        self, uow, sample_config, sample_geonames
    ):
        """Test saving and retrieving a Campaign with PlaceExtractionTasks."""
        # Arrange
        campaign = Campaign.create(title="Campaign with Tasks", config=sample_config)

        tasks = [
            PlaceExtractionTask.create(
                campaign_id=campaign.id,
                search_seed=seed,
                geoname=geoname,
            )
            for geoname in sample_geonames
            for seed in sample_config.search_seeds
        ]
        campaign.add_tasks(tasks)

        # Act - Save
        with uow:
            uow.campaign_repository.save(campaign)
            uow.commit()

        # Act - Retrieve
        with uow:
            retrieved = uow.campaign_repository.find_by_id(campaign.id)

        # Assert - Campaign
        assert retrieved is not None
        assert retrieved.title == "Campaign with Tasks"
        assert retrieved.total_tasks == 4  # 2 geonames × 2 seeds

        # Assert - Tasks
        assert len(retrieved.tasks) == 4
        task_titles = {t.title for t in retrieved.tasks}
        assert "restaurants Madrid" in task_titles
        assert "hotels Madrid" in task_titles
        assert "restaurants Barcelona" in task_titles
        assert "hotels Barcelona" in task_titles

        # Assert - Task details
        madrid_task = next(t for t in retrieved.tasks if "Madrid" in t.title)
        assert madrid_task.status == TaskStatus.PENDING
        assert madrid_task.geoname.latitude == 40.4168
        assert madrid_task.geoname.population == 3223334

    def test_update_campaign_status(self, uow, sample_config):
        """Test updating a Campaign's status."""
        # Arrange
        campaign = Campaign.create(title="Status Test", config=sample_config)

        with uow:
            uow.campaign_repository.save(campaign)
            uow.commit()

        # Act - Update status
        with uow:
            retrieved = uow.campaign_repository.find_by_id(campaign.id)
            retrieved.mark_in_progress()
            uow.campaign_repository.save(retrieved)
            uow.commit()

        # Assert
        with uow:
            updated = uow.campaign_repository.find_by_id(campaign.id)
            assert updated.status == CampaignStatus.IN_PROGRESS
            assert updated.started_at is not None

    def test_increment_completed_tasks(self, uow, sample_config):
        """Test atomic increment of completed_tasks counter."""
        # Arrange
        campaign = Campaign.create(title="Counter Test", config=sample_config)

        with uow:
            uow.campaign_repository.save(campaign)
            uow.commit()

        # Act - Increment
        with uow:
            uow.campaign_repository.increment_completed(campaign.id)
            uow.campaign_repository.increment_completed(campaign.id)
            uow.commit()

        # Assert
        with uow:
            updated = uow.campaign_repository.find_by_id(campaign.id)
            assert updated.completed_tasks == 2

    def test_increment_failed_tasks(self, uow, sample_config):
        """Test atomic increment of failed_tasks counter."""
        # Arrange
        campaign = Campaign.create(title="Counter Test", config=sample_config)

        with uow:
            uow.campaign_repository.save(campaign)
            uow.commit()

        # Act - Increment
        with uow:
            uow.campaign_repository.increment_failed(campaign.id)
            uow.commit()

        # Assert
        with uow:
            updated = uow.campaign_repository.find_by_id(campaign.id)
            assert updated.failed_tasks == 1

    def test_delete_campaign_cascades_to_tasks(
        self, uow, sample_config, sample_geonames
    ):
        """Test that deleting a Campaign also deletes its tasks."""
        # Arrange
        campaign = Campaign.create(title="Delete Test", config=sample_config)
        tasks = [
            PlaceExtractionTask.create(
                campaign_id=campaign.id,
                search_seed="restaurants",
                geoname=sample_geonames[0],
            )
        ]
        campaign.add_tasks(tasks)

        with uow:
            uow.campaign_repository.save(campaign)
            uow.commit()

        # Act - Delete
        with uow:
            uow.campaign_repository.delete(campaign.id)
            uow.commit()

        # Assert
        with uow:
            deleted = uow.campaign_repository.find_by_id(campaign.id)
            assert deleted is None

    def test_find_nonexistent_campaign_returns_none(self, uow):
        """Test that finding a non-existent Campaign returns None."""
        with uow:
            result = uow.campaign_repository.find_by_id(CampaignId.new())
            assert result is None

    def test_campaign_config_json_serialization(self, uow, sample_config):
        """Test that CampaignConfig is correctly serialized/deserialized to JSON."""
        # Arrange
        campaign = Campaign.create(title="JSON Test", config=sample_config)

        with uow:
            uow.campaign_repository.save(campaign)
            uow.commit()

        # Act
        with uow:
            retrieved = uow.campaign_repository.find_by_id(campaign.id)

        # Assert - All config fields preserved
        config = retrieved.config
        assert config.search_seeds == ("restaurants", "hotels")
        assert config.locale == "en-US"
        assert config.max_results == 100
        assert config.min_rating == 4.0
        assert config.max_total_workers == 30
        assert config.extraction_workers == 15

        # Assert - Nested geoname_selection_params
        params = config.geoname_selection_params
        assert params.scope_country_code == "ES"
        assert params.scope_geoname_id == 2510769
        assert params.min_population == 50000

        # Assert - Enrichment pools
        assert len(config.enrichment_pools) > 0
