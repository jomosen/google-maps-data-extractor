"""Bot Snapshot - Temporary state capture for UI monitoring"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from extraction.domain.enums.bot_status import BotStatus


@dataclass(frozen=True)
class BotSnapshot:
    """
    Value Object representing a point-in-time snapshot of a bot's state.
    
    Pure domain object - no presentation concerns (no base64, no JSON).
    The presentation layer is responsible for converting bytes to appropriate format.
    
    Used for UI monitoring - NOT persisted to database.
    """
    bot_id: str
    status: BotStatus
    screenshot_bytes: bytes  # Raw bytes, NOT base64 (domain doesn't know about encoding)
    current_url: str
    captured_at: datetime
    current_task_id: Optional[str] = None
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None
    
    @staticmethod
    def create(
        bot_id: str, 
        status: BotStatus, 
        screenshot_bytes: bytes, 
        url: str, 
        task_id: Optional[str] = None
    ) -> "BotSnapshot":
        """
        Factory method for creating snapshots.
        
        Args:
            bot_id: Unique bot identifier
            status: Current bot status
            screenshot_bytes: Raw screenshot bytes (PNG/JPEG format)
            url: Current page URL
            task_id: Optional current task ID
            
        Returns:
            Immutable BotSnapshot instance
        """
        return BotSnapshot(
            bot_id=bot_id,
            status=status,
            screenshot_bytes=screenshot_bytes,
            current_url=url,
            current_task_id=task_id,
            captured_at=datetime.now()
        )
