"""
Bot Snapshot DTO - Data Transfer Object for Presentation Layer

This DTO represents how bot snapshots are exposed to external consumers (WebSocket, REST API).
It's decoupled from domain models and can evolve independently.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class BotSnapshotDTO:
    """
    DTO for bot snapshot in presentation layer.
    
    Differences from domain BotSnapshot:
    - status: string instead of enum (JSON-friendly)
    - screenshot: base64 string instead of bytes (WebSocket-friendly)
    - No datetime objects (converted to ISO strings if needed)
    
    This DTO can be easily serialized to JSON and sent over WebSocket.
    """
    bot_id: str
    status: str
    screenshot: str  # Base64-encoded screenshot
    current_url: str
    task_id: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert DTO to dictionary for JSON serialization."""
        return {
            "bot_id": self.bot_id,
            "status": self.status,
            "screenshot": self.screenshot,
            "current_url": self.current_url,
            "task_id": self.task_id,
        }
