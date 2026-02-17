"""
Event Bus - Central event dispatcher for Domain Events

Implements the Observer pattern to allow domain entities to publish events
and application/presentation layers to subscribe to them.
"""
import asyncio
from typing import Dict, List, Callable, Type, Any
from collections import defaultdict
from shared.logging import get_logger


class EventBus:
    """
    Central event bus for publishing and subscribing to domain events.
    
    Features:
    - Type-based subscription (subscribe to specific event types)
    - Async event handling
    - Multiple subscribers per event type
    - Error isolation (one handler failure doesn't affect others)
    
    Usage:
        # Subscribe
        event_bus.subscribe(BotInitializedEvent, handle_bot_initialized)
        
        # Publish
        await event_bus.publish(BotInitializedEvent(bot_id="123"))
    """
    
    def __init__(self):
        """Initialize empty subscriber registry"""
        self._subscribers: Dict[Type, List[Callable]] = defaultdict(list)
    
    def subscribe(self, event_type: Type, handler: Callable) -> None:
        """
        Subscribe to a specific event type.
        
        Args:
            event_type: The event class to subscribe to
            handler: Async callable that will receive the event
            
        Example:
            async def on_bot_ready(event: BotInitializedEvent):
                print(f"Bot {event.bot_id} is ready")
            
            event_bus.subscribe(BotInitializedEvent, on_bot_ready)
        """
        self._subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: Type, handler: Callable) -> None:
        """
        Unsubscribe a handler from an event type.
        
        Args:
            event_type: The event class to unsubscribe from
            handler: The handler to remove
        """
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                h for h in self._subscribers[event_type] if h != handler
            ]
    
    async def publish(self, event: Any) -> None:
        """
        Publish an event to all subscribers.
        
        Handlers are executed concurrently. If a handler raises an exception,
        it's caught and logged, but other handlers continue execution.
        
        Args:
            event: The event instance to publish
            
        Example:
            await event_bus.publish(
                BotInitializedEvent(bot_id="123", occurred_at=datetime.now())
            )
        """
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])
        
        if not handlers:
            # No subscribers for this event type
            return
        
        # Execute all handlers concurrently, capturing exceptions
        results = await asyncio.gather(
            *[self._safe_handle(handler, event) for handler in handlers],
            return_exceptions=True
        )
        
        # Log any errors
        logger = get_logger(__name__)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    "event_handler_failed",
                    handler_name=handlers[i].__name__,
                    event_type=event_type.__name__,
                    error=str(result),
                    error_type=type(result).__name__
                )
    
    async def _safe_handle(self, handler: Callable, event: Any) -> None:
        """
        Execute a handler safely, wrapping sync handlers in async.
        
        Args:
            handler: The event handler to execute
            event: The event to pass to the handler
        """
        if asyncio.iscoroutinefunction(handler):
            await handler(event)
        else:
            handler(event)
    
    def clear_all_subscriptions(self) -> None:
        """Clear all subscriptions. Useful for testing."""
        self._subscribers.clear()
    
    def get_subscriber_count(self, event_type: Type) -> int:
        """Get number of subscribers for an event type. Useful for testing."""
        return len(self._subscribers.get(event_type, []))
