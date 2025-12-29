from typing import Protocol, Optional
from extraction.domain.enums.campaign_status import CampaignStatus
from extraction.domain.campaign import Campaign


class CampaignRepository(Protocol):
    """
    Port for persisting and retrieving ExtractionJob aggregate roots.
    Implementations live in the infrastructure layer.
    """

    def save(self, job: Campaign) -> None:
        """
        Persist the ExtractionJob aggregate.
        Implementations should perform insert/update as needed.
        """
        ...

    def find_all(self) -> list[Campaign]:
        """
        Retrieve all ExtractionJobs.
        """
        ...

    def find_by_id(self, job_id: str) -> Optional[Campaign]:
        """
        Retrieve an ExtractionJob by its ID.
        Return None if not found.
        """
        ...

    def find_pending(self) -> list[Campaign]:
        """
        Retrieve all ExtractionJobs that are not completed.
        """
        ...

    def delete(self, job_id: str) -> None:
        """
        Delete the ExtractionJob by ID.
        Optional in many systems but good to define.
        """
        ...

    def save_status(self, job: Campaign) -> None:
        """
        Save the status of the ExtractionJob.
        """
        ...

    def increment_completed(self, job_id: str) -> None:
        """
        Increment the count of completed tasks for the ExtractionJob.
        """
        ...

    def increment_failed(self, job_id: str) -> None:
        """
        Increment the count of failed tasks for the ExtractionJob.
        """
        ...

