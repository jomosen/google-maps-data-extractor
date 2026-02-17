"""Domain enums for extraction BC."""

from .campaign_scope import CampaignScope
from .campaign_depth_level import CampaignDepthLevel
from .campaign_status import CampaignStatus
from .task_status import TaskStatus
from .bot_status import BotStatus
from .enrichment_type import EnrichmentType
from .enrichment_status import EnrichmentStatus

__all__ = [
    "CampaignScope",
    "CampaignDepthLevel",
    "CampaignStatus",
    "TaskStatus",
    "BotStatus",
    "EnrichmentType",
    "EnrichmentStatus",
]
