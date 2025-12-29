from dataclasses import dataclass


@dataclass(frozen=True)
class PlaceExtractionContext:
    
    task_id: str
    postal_code_regex: str
