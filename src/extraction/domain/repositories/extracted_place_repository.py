from abc import ABC, abstractmethod
from extraction.domain.extracted_place import ExtractedPlace


class ExtractedPlaceRepository(ABC):
    
    @abstractmethod
    def save(self, place: ExtractedPlace) -> None:
        pass

    @abstractmethod
    def exists_by_place_id(self, place_id: str) -> bool:
        pass