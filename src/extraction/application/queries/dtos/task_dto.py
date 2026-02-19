"""DTO for extraction task list view."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TaskDto:
    """Application-layer DTO for extraction task list view."""

    task_id: str
    search_seed: str
    geoname_name: str
    status: str
    attempts: int
    last_error: str | None
    created_at: datetime
