"""Task Queue - Application Service for managing extraction task queue"""
import asyncio
from typing import List

from shared.logging import get_logger
from extraction.domain.entities.place_extraction_task import PlaceExtractionTask


class TaskQueue:
    """
    Application Service that manages the queue of extraction tasks.
    
    Responsibilities (SRP):
    - Enqueue tasks (FIFO order)
    - Dequeue next task (blocking if empty)
    - Query queue state (pending count, has tasks)
    
    This service implements a simple FIFO strategy.
    If we need priority-based queuing (e.g., by population, country),
    this could evolve into a Domain Service with business rules.
    
    Uses asyncio.Queue for thread-safe async operations.
    """

    def __init__(self):
        """Initialize empty task queue."""
        self._queue: asyncio.Queue[PlaceExtractionTask] = asyncio.Queue()

    async def enqueue(self, task: PlaceExtractionTask) -> None:
        """
        Add a single task to the queue.
        
        Args:
            task: Extraction task to enqueue
        """
        await self._queue.put(task)

    async def enqueue_many(self, tasks: List[PlaceExtractionTask]) -> None:
        """
        Add multiple tasks to the queue.
        
        Args:
            tasks: List of extraction tasks to enqueue
        """
        logger = get_logger(__name__)
        for task in tasks:
            await self._queue.put(task)
        logger.info("tasks_enqueued", count=len(tasks))

    async def dequeue(self) -> PlaceExtractionTask:
        """
        Get the next task from the queue.
        
        This operation blocks if the queue is empty until a task is available.
        
        Returns:
            Next extraction task in FIFO order
        """
        return await self._queue.get()

    def has_pending_tasks(self) -> bool:
        """
        Check if there are pending tasks in the queue.
        
        Returns:
            True if queue has at least one task, False otherwise
        """
        return not self._queue.empty()

    def pending_count(self) -> int:
        """
        Get the number of pending tasks in the queue.
        
        Returns:
            Number of tasks waiting in the queue
        """
        return self._queue.qsize()
