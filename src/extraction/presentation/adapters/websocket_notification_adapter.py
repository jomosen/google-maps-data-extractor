"""
WebSocket Notification Adapter - Concrete implementation of BotNotificationInterface

This adapter implements the notification interface using WebSocket as the delivery mechanism.
It converts domain objects to DTOs and then to WebSocket messages (JSON).
"""
from typing import Optional
from fastapi import WebSocket

from extraction.application.interfaces.bot_notification_interface import BotNotificationInterface
from extraction.domain.value_objects.bot_snapshot import BotSnapshot
from extraction.presentation.dto import bot_snapshot_to_dto


class WebSocketNotificationAdapter(BotNotificationInterface):
    """
    Adapter that implements bot notifications using WebSocket.
    
    Responsibilities:
    - Convert domain objects to presentation DTOs (using mappers)
    - Convert DTOs to WebSocket message format (JSON)
    - Send messages through the WebSocket connection
    
    This adapter lives in the presentation layer and is responsible for
    the Anti-Corruption Layer between domain and external protocols.
    """
    
    def __init__(self, websocket: WebSocket):
        """
        Initialize the adapter with a WebSocket connection.
        
        Args:
            websocket: Active WebSocket connection to send messages through
        """
        self.websocket = websocket
    
    async def notify_bot_initialized(self, bot_id: str) -> None:
        """Send bot initialized notification via WebSocket"""
        await self.websocket.send_json({
            "type": "bot_status",
            "data": {
                "bot_id": bot_id,
                "status": "idle",
                "message": "Bot initialized"
            }
        })
    
    async def notify_bot_snapshot(self, snapshot: BotSnapshot) -> None:
        """
        Send bot snapshot via WebSocket.
        
        Converts the domain BotSnapshot to DTO (with base64 encoding),
        then to WebSocket message format.
        """
        # Convert domain object to presentation DTO
        dto = bot_snapshot_to_dto(snapshot)
        
        await self.websocket.send_json({
            "type": "bot_snapshot",
            "data": {
                "bot_id": dto.bot_id,
                "status": dto.status,
                "screenshot": dto.screenshot,  # Already base64 from mapper
                "current_url": dto.current_url,
                "task_id": dto.task_id,
            }
        })
    
    async def notify_bot_task_assigned(self, bot_id: str, task_id: str) -> None:
        """Send task assigned notification via WebSocket"""
        await self.websocket.send_json({
            "type": "bot_status",
            "data": {
                "bot_id": bot_id,
                "status": "processing",
                "task_id": task_id,
                "message": "Task assigned"
            }
        })
    
    async def notify_bot_task_completed(self, bot_id: str, task_id: str) -> None:
        """Send task completed notification via WebSocket"""
        await self.websocket.send_json({
            "type": "bot_status",
            "data": {
                "bot_id": bot_id,
                "status": "idle",
                "task_id": task_id,
                "message": "Task completed"
            }
        })
    
    async def notify_bot_error(self, bot_id: str, error: str) -> None:
        """Send bot error notification via WebSocket"""
        await self.websocket.send_json({
            "type": "bot_error",
            "data": {
                "bot_id": bot_id,
                "error": error,
            }
        })
    
    async def notify_bot_closed(self, bot_id: str) -> None:
        """Send bot closed notification via WebSocket"""
        await self.websocket.send_json({
            "type": "bot_status",
            "data": {
                "bot_id": bot_id,
                "status": "closed",
            }
        })
