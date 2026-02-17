"""
Bot Notification Interface - Output Port for bot state notifications

This interface defines WHAT events can be notified about bots,
but not HOW they are delivered (WebSocket, email, log, etc.)

Following Dependency Inversion Principle, the application layer defines
this interface and the presentation layer provides concrete implementations.
"""
from abc import ABC, abstractmethod
from typing import Optional

from ...domain.value_objects.bot_snapshot import BotSnapshot


class BotNotificationInterface(ABC):
    """
    Output Port interface for notifying about bot state changes.
    
    The application layer uses this interface to notify external systems
    about bot events without depending on specific delivery mechanisms.
    
    Benefits:
    - Application remains decoupled from presentation details
    - Easy to test with mock implementations
    - Can have multiple implementations (WebSocket, logging, email, etc.)
    - Follows Dependency Inversion Principle
    """
    
    @abstractmethod
    async def notify_bot_initialized(self, bot_id: str) -> None:
        """
        Notify when a bot has been initialized and is ready to work.
        
        Args:
            bot_id: Unique identifier of the bot
        """
        pass
    
    @abstractmethod
    async def notify_bot_snapshot(self, snapshot: BotSnapshot) -> None:
        """
        Notify when a bot snapshot is available (screenshot, state update).
        
        Args:
            snapshot: Bot snapshot containing current state and screenshot
        """
        pass
    
    @abstractmethod
    async def notify_bot_task_assigned(self, bot_id: str, task_id: str) -> None:
        """
        Notify when a task has been assigned to a bot.
        
        Args:
            bot_id: Unique identifier of the bot
            task_id: Unique identifier of the assigned task
        """
        pass
    
    @abstractmethod
    async def notify_bot_task_completed(self, bot_id: str, task_id: str) -> None:
        """
        Notify when a bot has completed a task.
        
        Args:
            bot_id: Unique identifier of the bot
            task_id: Unique identifier of the completed task
        """
        pass
    
    @abstractmethod
    async def notify_bot_error(self, bot_id: str, error: str) -> None:
        """
        Notify when a bot encounters an error.
        
        Args:
            bot_id: Unique identifier of the bot
            error: Error message or description
        """
        pass
    
    @abstractmethod
    async def notify_bot_closed(self, bot_id: str) -> None:
        """
        Notify when a bot has been closed/terminated.
        
        Args:
            bot_id: Unique identifier of the bot
        """
        pass
