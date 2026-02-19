"""DTOs for campaign query results."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CampaignDto:
    """Application-layer DTO for campaign queries (list and detail)."""

    campaign_id: str
    title: str
    status: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    max_bots: int
    activity: str
    location_name: str

    @property
    def completion_percentage(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return round((self.completed_tasks / self.total_tasks) * 100, 1)
