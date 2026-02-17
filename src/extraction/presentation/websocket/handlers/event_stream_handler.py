"""
Event Stream Handler - Handles real-time event streaming

Event streaming follows pub/sub pattern:
- Subscribes to domain events
- Streams events in real-time to WebSocket clients
- Converts domain events to DTOs for presentation
"""
import asyncio
from typing import cast
from fastapi import WebSocket

from shared.logging import get_logger
from shared.events import EventBus
from extraction.presentation.adapters import WebSocketNotificationAdapter
from extraction.domain.events import (
    BotInitializedEvent,
    BotSnapshotCapturedEvent,
    BotTaskAssignedEvent,
    BotTaskCompletedEvent,
    BotErrorEvent,
    BotClosedEvent,
    TaskStartedEvent,
    TaskCompletedEvent,
    TaskFailedEvent
)


class EventStreamHandler:
    """
    Handles real-time event streaming to WebSocket clients.
    
    Subscribes to domain events and forwards them to clients
    with appropriate formatting and rate limiting.
    
    This is the "push" mechanism in the CQRS pattern.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    async def start_streaming(
        self, 
        websocket: WebSocket, 
        event_bus: EventBus
    ) -> None:
        """
        Start streaming domain events to WebSocket client.
        
        Subscribes to all relevant domain events and forwards them
        to the client in real-time.
        
        Args:
            websocket: Active WebSocket connection
            event_bus: Event bus with domain events
        """
        self.logger.info("event_streaming_started")
        
        # Create WebSocket notification adapter
        notification_adapter = WebSocketNotificationAdapter(websocket)
        
        # Subscribe to all domain events
        self._subscribe_to_events(event_bus, notification_adapter)
        
        # Send streaming started confirmation
        await websocket.send_json({
            "type": "stream_started",
            "message": "Event streaming active"
        })
    
    def _subscribe_to_events(
        self, 
        event_bus: EventBus, 
        adapter: WebSocketNotificationAdapter
    ) -> None:
        """
        Subscribe to all domain events and forward to WebSocket adapter.
        
        Uses asyncio.create_task() to schedule async adapter methods
        without blocking event publication.
        """
        # Bot events
        event_bus.subscribe(
            BotInitializedEvent,
            lambda event: asyncio.create_task(
                adapter.notify_bot_initialized(cast(BotInitializedEvent, event).bot_id)
            )
        )
        
        event_bus.subscribe(
            BotSnapshotCapturedEvent,
            lambda event: asyncio.create_task(
                adapter.notify_bot_snapshot(cast(BotSnapshotCapturedEvent, event).snapshot)
            )
        )
        
        event_bus.subscribe(
            BotTaskAssignedEvent,
            lambda event: asyncio.create_task(
                adapter.notify_bot_task_assigned(
                    cast(BotTaskAssignedEvent, event).bot_id,
                    cast(BotTaskAssignedEvent, event).task_id
                )
            )
        )
        
        event_bus.subscribe(
            BotTaskCompletedEvent,
            lambda event: asyncio.create_task(
                adapter.notify_bot_task_completed(
                    cast(BotTaskCompletedEvent, event).bot_id,
                    cast(BotTaskCompletedEvent, event).task_id
                )
            )
        )
        
        event_bus.subscribe(
            BotErrorEvent,
            lambda event: asyncio.create_task(
                adapter.notify_bot_error(
                    cast(BotErrorEvent, event).bot_id,
                    cast(BotErrorEvent, event).error
                )
            )
        )
        
        event_bus.subscribe(
            BotClosedEvent,
            lambda event: asyncio.create_task(
                adapter.notify_bot_closed(cast(BotClosedEvent, event).bot_id)
            )
        )
        
        # Task events (optional - for future use)
        # event_bus.subscribe(TaskStartedEvent, lambda event: ...)
        # event_bus.subscribe(TaskCompletedEvent, lambda event: ...)
        # event_bus.subscribe(TaskFailedEvent, lambda event: ...)
        
        self.logger.info("event_subscriptions_registered")
