"""Bot Entity - Ephemeral worker that processes extraction tasks"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from ..enums.bot_status import BotStatus
from ..value_objects.ids import BotId, ExtractionTaskId
from ..value_objects.bot_snapshot import BotSnapshot
from ..entities.place_extraction_task import PlaceExtractionTask
from ..exceptions import BotError
from ..events import (
    BotInitializedEvent,
    BotSnapshotCapturedEvent,
    BotTaskAssignedEvent,
    BotTaskCompletedEvent,
    BotErrorEvent,
    BotClosedEvent
)
from shared.events import EventBus


class Bot:
    """
    Bot Entity - Represents an ephemeral browser worker.
    
    Bots are NOT persisted to database - they only exist in memory during execution.
    They process PlaceExtractionTask instances which ARE persisted.
    
    Lifecycle:
    1. INITIALIZING → Browser launching
    2. IDLE → Ready to process tasks
    3. PROCESSING_TASK → Extracting places from Google Maps
    4. IDLE → Task completed, ready for next
    5. CLOSED → Browser closed, bot terminated
    
    Domain Invariants:
    - Can only assign task when IDLE or already PROCESSING_TASK
    - Can only complete task when PROCESSING_TASK
    - Can transition to ERROR from any state
    
    Domain Events:
    - Emits events on state changes for interested subscribers
    """

    def __init__(self, bot_id: BotId, event_bus: EventBus):
        self.id = bot_id
        self.event_bus = event_bus
        self.status = BotStatus.INITIALIZING
        self.current_task: Optional[PlaceExtractionTask] = None
        self.last_snapshot: Optional[BotSnapshot] = None
        self.started_at: datetime = datetime.now()
        self.last_activity_at: datetime = datetime.now()
        self._error_message: Optional[str] = None

    @staticmethod
    def create(event_bus: EventBus) -> "Bot":
        """Factory method to create a new bot."""
        return Bot(BotId.new(), event_bus)

    # =================================================================
    # State Transitions
    # =================================================================

    def mark_as_ready(self) -> None:
        """
        Mark bot as ready after browser initialization.
        
        Raises:
            BotError: If not in INITIALIZING state
        """
        if self.status != BotStatus.INITIALIZING:
            raise BotError(
                f"Can only mark ready from INITIALIZING state, current: {self.status}"
            )
        
        self.status = BotStatus.IDLE
        self.last_activity_at = datetime.now()
        
        # Emit event
        asyncio.create_task(self.event_bus.publish(
            BotInitializedEvent(
                occurred_at=datetime.now(),
                aggregate_id=str(self.id),
                bot_id=str(self.id)
            )
        ))

    def assign_task(self, task: PlaceExtractionTask) -> None:
        """
        Assign a task to this bot.
        
        Raises:
            BotError: If bot is not in valid state to accept task
        """
        if self.status not in [BotStatus.IDLE, BotStatus.PROCESSING_TASK]:
            raise BotError(
                f"Cannot assign task in state {self.status}. Must be IDLE or PROCESSING_TASK"
            )
        
        self.current_task = task
        self.status = BotStatus.PROCESSING_TASK
        self.last_activity_at = datetime.now()
        
        # Emit event
        asyncio.create_task(self.event_bus.publish(
            BotTaskAssignedEvent(
                occurred_at=datetime.now(),
                aggregate_id=str(self.id),
                bot_id=str(self.id),
                task_id=str(task.id)
            )
        ))

    def update_snapshot(self, snapshot: BotSnapshot) -> None:
        """
        Update bot's current snapshot (for UI monitoring).
        
        This is called periodically during task processing to provide
        real-time browser screenshots to the frontend.
        """
        self.last_snapshot = snapshot
        self.last_activity_at = datetime.now()
        
        # Emit event
        asyncio.create_task(self.event_bus.publish(
            BotSnapshotCapturedEvent(
                occurred_at=datetime.now(),
                aggregate_id=str(self.id),
                bot_id=str(self.id),
                snapshot=snapshot
            )
        ))

    def complete_task(self) -> None:
        """
        Mark current task as completed and return to IDLE state.
        
        Note: The task itself is updated separately in the repository.
        Bot just releases the reference and becomes available for next task.
        
        Raises:
            BotError: If not currently processing a task
        """
        if self.status != BotStatus.PROCESSING_TASK:
            raise BotError(
                f"Can only complete task from PROCESSING_TASK state, current: {self.status}"
            )
        
        if self.current_task is None:
            raise BotError("No task assigned to complete")
        
        completed_task_id = str(self.current_task.id)
        self.current_task = None
        self.status = BotStatus.IDLE
        self.last_activity_at = datetime.now()
        
        # Emit event
        asyncio.create_task(self.event_bus.publish(
            BotTaskCompletedEvent(
                occurred_at=datetime.now(),
                aggregate_id=str(self.id),
                bot_id=str(self.id),
                task_id=completed_task_id
            )
        ))

    def mark_as_error(self, error_message: str) -> None:
        """
        Mark bot as ERROR state.
        
        Can be called from any state when an unrecoverable error occurs.
        """
        self.status = BotStatus.ERROR
        self._error_message = error_message
        self.last_activity_at = datetime.now()
        
        # Emit event
        asyncio.create_task(self.event_bus.publish(
            BotErrorEvent(
                occurred_at=datetime.now(),
                aggregate_id=str(self.id),
                bot_id=str(self.id),
                error=error_message
            )
        ))

    def close(self) -> None:
        """
        Close bot and release all resources.
        
        After calling this, bot should not be used anymore.
        """
        self.status = BotStatus.CLOSED
        self.current_task = None
        self.last_activity_at = datetime.now()
        
        # Emit event
        asyncio.create_task(self.event_bus.publish(
            BotClosedEvent(
                occurred_at=datetime.now(),
                aggregate_id=str(self.id),
                bot_id=str(self.id)
            )
        ))
        self.last_snapshot = None
        self.last_activity_at = datetime.now()

    # =================================================================
    # BUSINESS RULES (Query Methods)
    # =================================================================

    def can_accept_task(self) -> bool:
        """
        Check if bot can accept a new task.
        
        Business rule: Bot must be in IDLE state.
        
        Returns:
            True if bot can accept task assignment
        """
        return self.status == BotStatus.IDLE

    def has_been_idle_for(self, minutes: int) -> bool:
        """
        Check if bot has been idle for specified duration.
        
        Useful for detecting stuck bots or implementing timeouts.
        
        Args:
            minutes: Idle duration threshold in minutes
            
        Returns:
            True if bot has been idle for longer than threshold
        """
        if self.status != BotStatus.IDLE:
            return False
        
        idle_duration = datetime.now() - self.last_activity_at
        return idle_duration > timedelta(minutes=minutes)

    def is_healthy(self) -> bool:
        """
        Check if bot is in healthy operational state.
        
        Business rule: Bot should not be in ERROR or CLOSED state.
        
        Returns:
            True if bot can continue working
        """
        return self.status not in [BotStatus.ERROR, BotStatus.CLOSED]

    def uptime_seconds(self) -> float:
        """
        Get bot uptime in seconds.
        
        Returns:
            Seconds since bot was created
        """
        return (datetime.now() - self.started_at).total_seconds()

    # =================================================================
    # Query Methods
    # =================================================================

    @property
    def is_available(self) -> bool:
        """Check if bot is available to process tasks."""
        return self.status == BotStatus.IDLE

    @property
    def is_processing(self) -> bool:
        """Check if bot is currently processing a task."""
        return self.status == BotStatus.PROCESSING_TASK

    @property
    def has_error(self) -> bool:
        """Check if bot is in error state."""
        return self.status == BotStatus.ERROR

    @property
    def error_message(self) -> Optional[str]:
        """Get error message if bot is in error state."""
        return self._error_message

    @property
    def current_task_id(self) -> Optional[ExtractionTaskId]:
        """Get ID of currently assigned task."""
        return self.current_task.id if self.current_task else None

    def __repr__(self) -> str:
        task_info = f"task={self.current_task_id}" if self.current_task else "no_task"
        return f"Bot(id={self.id}, status={self.status}, {task_info})"
