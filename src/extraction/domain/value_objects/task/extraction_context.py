from dataclasses import dataclass
from ..ids import ExtractionTaskId


@dataclass(frozen=True)
class PlaceExtractionContext:

    task_id: ExtractionTaskId
    postal_code_regex: str
