"""
Bot Domain Events - Events emitted by Bot aggregate

These events represent state changes in the Bot lifecycle.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .domain_event import DomainEvent
from ..value_objects.bot_snapshot import BotSnapshot


@dataclass
class BotInitializedEvent(DomainEvent):
    """
    Event: Bot was successfully initialized and is ready to work.
    
    Emitted by: Bot.mark_as_ready()
    Interested parties: WebSocket clients, monitoring
    """
    bot_id: str


@dataclass
class BotSnapshotCapturedEvent(DomainEvent):
    """
    Event: Bot captured a screenshot of its current state.
    
    Emitted by: Bot.update_snapshot()
    Interested parties: WebSocket clients (real-time UI updates)
    """
    bot_id: str
    snapshot: BotSnapshot


@dataclass
class BotTaskAssignedEvent(DomainEvent):
    """
    Event: A task was assigned to the bot.
    
    Emitted by: Bot.assign_task()
    Interested parties: WebSocket clients, monitoring
    """
    bot_id: str
    task_id: str


@dataclass
class BotTaskCompletedEvent(DomainEvent):
    """
    Event: Bot finished processing its assigned task.
    
    Note: This doesn't mean the task is complete, just that the bot
    finished its work. The task itself emits TaskCompletedEvent.
    
    Emitted by: Bot.complete_task()
    Interested parties: BotOrchestrator (for task reassignment), monitoring
    """
    bot_id: str
    task_id: str


@dataclass
class BotErrorEvent(DomainEvent):
    """
    Event: Bot encountered an error during processing.
    
    Emitted by: Bot.mark_as_error()
    Interested parties: WebSocket clients, logging, alerting
    """
    bot_id: str
    error: str


@dataclass
class BotClosedEvent(DomainEvent):
    """
    Event: Bot was closed and resources released.
    
    Emitted by: Bot.close()
    Interested parties: Monitoring, resource cleanup
    """
    bot_id: str
