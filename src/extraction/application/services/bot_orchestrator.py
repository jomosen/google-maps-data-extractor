"""Bot Orchestrator - Application Service for orchestrating extraction process"""
import asyncio
from typing import List

from shared.logging import get_logger
from extraction.domain.entities.place_extraction_task import PlaceExtractionTask
from extraction.domain.value_objects import BotSnapshot
from extraction.application.services.bot_pool_manager import BotPoolManager
from extraction.application.services.task_queue import TaskQueue


class BotOrchestrator:
    """
    Application Service that orchestrates the extraction process.
    
    Single Responsibility (SRP):
    - Coordinate assignment of tasks from TaskQueue to bots from BotPoolManager
    - Execute main extraction loop
    - Wait for all bots to complete their work
    
    This service does NOT:
    - Create/close bots (delegated to BotPoolManager)
    - Manage task queue (delegated to TaskQueue)
    - Emit domain events (delegated to Bot and Task entities)
    
    By extracting bot pool and task queue management to separate services,
    we achieve better separation of concerns and testability.
    
    Dependencies are injected following Dependency Inversion Principle.
    """

    def __init__(
        self,
        bot_pool_manager: BotPoolManager,
        task_queue: TaskQueue
    ):
        """
        Initialize the bot orchestrator.
        
        Args:
            bot_pool_manager: Service that manages bot pool lifecycle
            task_queue: Service that manages task queue
        """
        self.bot_pool_manager = bot_pool_manager
        self.task_queue = task_queue

    async def start_extraction(
        self,
        tasks: List[PlaceExtractionTask]
    ) -> None:
        """
        Start extraction process.
        
        Flow:
        1. Enqueue all tasks into TaskQueue
        2. Assign tasks to bots (round-robin from pool)
        3. Process all tasks concurrently
        4. Cleanup (done by BotPoolManager)
        
        Args:
            tasks: List of extraction tasks to process
        """
        logger = get_logger(__name__)
        logger.info("orchestrator_start", num_tasks=len(tasks))
        
        try:
            # Enqueue all tasks
            await self.task_queue.enqueue_many(tasks)
            
            # Assign tasks to bots and process
            await self._assign_and_process_tasks(tasks)
            
            logger.info("orchestrator_completed")
            
        finally:
            # Cleanup: close all bots
            await self.bot_pool_manager.close_all()

    async def _assign_and_process_tasks(
        self,
        tasks: List[PlaceExtractionTask]
    ) -> None:
        """
        Assign tasks to bots from pool and start processing.
        
        Uses round-robin assignment strategy.
        """
        # Get all bots from pool
        bots = self.bot_pool_manager.get_all_bots()
        
        # Create processing coroutines for each bot-task pair
        processing_tasks = []
        
        for idx, task in enumerate(tasks):
            bot = bots[idx % len(bots)]  # Round-robin assignment
            
            # Mark task as started (will emit TaskStartedEvent)
            task.mark_in_progress()
            
            # Assign to bot (will emit BotTaskAssignedEvent)
            bot.assign_task(task)
            
            processing_task = self._process_task_with_bot(bot, task)
            processing_tasks.append(processing_task)
        
        # Run all bots concurrently
        await asyncio.gather(*processing_tasks, return_exceptions=True)

    async def _process_task_with_bot(
        self,
        bot,
        task: PlaceExtractionTask
    ) -> None:
        """
        Process a single task with a bot.
        
        For now: just navigate to Google Maps and stream screenshots.
        
        Args:
            bot: Bot entity that will process the task
            task: Extraction task to process
        """
        logger = get_logger(__name__)
        
        # Get driver from pool manager
        driver = self.bot_pool_manager.get_driver(str(bot.id))
        if not driver:
            error_msg = f"No driver found for bot {bot.id}"
            logger.error("bot_driver_not_found", bot_id=str(bot.id), task_id=str(task.id))
            bot.mark_as_error(error_msg)
            task.mark_failed(error_msg)
            return
        
        try:
            # Build Google Maps URL using task properties
            query = f"{task.search_seed} in {task.geoname.name}"
            gmaps_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
            
            logger.info(
                "bot_task_starting",
                bot_id=str(bot.id),
                task_id=str(task.id),
                geoname=task.geoname.name,
                search_seed=task.search_seed
            )
            
            # Navigate to Google Maps
            await driver.navigate_to(gmaps_url)
            
            # Give page time to load before first screenshot
            await asyncio.sleep(2)
            
            # Screenshot streaming loop (limited to 30 screenshots = 90 seconds for demo)
            screenshot_count = 0
            max_screenshots = 30
            
            while bot.is_processing and screenshot_count < max_screenshots:
                # Capture screenshot (raw bytes)
                screenshot_bytes = await driver.take_screenshot()
                
                # Get current URL (NOT async)
                current_url = driver.get_page_url()
                
                # Create snapshot using factory method with RAW BYTES (not base64)
                # Presentation layer will handle encoding via mapper
                snapshot = BotSnapshot.create(
                    bot_id=str(bot.id),
                    status=bot.status,
                    screenshot_bytes=screenshot_bytes,  # Raw bytes, domain doesn't know about base64
                    url=current_url,
                    task_id=str(task.id)
                )
                
                # Update snapshot (will emit BotSnapshotCapturedEvent)
                bot.update_snapshot(snapshot)
                
                screenshot_count += 1
                
                # Wait before next screenshot
                await asyncio.sleep(3)
            
            logger.info(
                "bot_task_completed",
                bot_id=str(bot.id),
                task_id=str(task.id),
                screenshots_captured=screenshot_count
            )
            
            # Mark task as completed (will emit TaskCompletedEvent)
            task.mark_completed()
            
            # Mark bot as done (will emit BotTaskCompletedEvent)
            bot.complete_task()
                
        except Exception as e:
            logger.error(
                "bot_task_failed",
                bot_id=str(bot.id),
                task_id=str(task.id),
                error=str(e),
                error_type=type(e).__name__
            )
            # Mark task as failed (will emit TaskFailedEvent)
            task.mark_failed(str(e))
            # Mark bot as error (will emit BotErrorEvent)
            bot.mark_as_error(str(e))
