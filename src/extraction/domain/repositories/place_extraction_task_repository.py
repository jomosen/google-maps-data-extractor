from abc import ABC, abstractmethod
from extraction.domain.place_extraction_task import PlaceExtractionTask


class PlaceExtractionTaskRepository(ABC):
    
    @abstractmethod
    def save(self, task: PlaceExtractionTask) -> None:
        pass

    @abstractmethod
    def find_by_id(self, task_id: str) -> PlaceExtractionTask | None:
        pass

    @abstractmethod
    def find_running(self, job_id: int) -> list[PlaceExtractionTask]:
        pass

    @abstractmethod
    def claim_next_pending(self, job_id: int, max_attempts: int) -> PlaceExtractionTask | None:
        pass