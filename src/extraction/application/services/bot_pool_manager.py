"""Bot Pool Manager - Application Service for managing bot lifecycle"""
import asyncio
import random
from typing import List, Dict, Optional

from shared.logging import get_logger
from extraction.domain.entities import Bot
from extraction.domain.value_objects import BrowserDriverConfig
from extraction.application.interfaces import (
    BrowserDriverFactoryInterface,
    BrowserDriverInterface
)
from shared.events import EventBus


class BotPoolManager:
    """
    Application Service that manages the lifecycle of a bot pool.
    
    Responsibilities (SRP):
    - Initialize bot pool with staggered delays (anti-detection)
    - Maintain registry of active bots and their drivers
    - Provide available bot from pool
    - Close all bots and release resources
    
    This service encapsulates all bot pool management logic,
    separating it from task assignment and orchestration logic.
    """

    def __init__(
        self,
        browser_driver_factory: BrowserDriverFactoryInterface,
        event_bus: EventBus,
        browser_config: BrowserDriverConfig = None
    ):
        """
        Initialize the bot pool manager.
        
        Args:
            browser_driver_factory: Factory for creating browser drivers (DIP)
            event_bus: Event bus for domain events
            browser_config: Configuration for browser drivers
        """
        self.browser_driver_factory = browser_driver_factory
        self.event_bus = event_bus
        self.browser_config = browser_config or BrowserDriverConfig(
            headless=False,
            timeout=30,
            locale="en-US"
        )
        
        self.bots: List[Bot] = []
        self.drivers: Dict[str, BrowserDriverInterface] = {}  # bot_id -> driver

    async def initialize_pool(
        self,
        num_bots: int,
        stagger_delay_range: tuple[float, float] = (2.0, 5.0)
    ) -> None:
        """
        Initialize bot pool with staggered browser launches.
        
        Staggered delays help avoid detection by making bot launches
        appear more human-like and distributed over time.
        
        Args:
            num_bots: Number of bots to create
            stagger_delay_range: (min, max) delay in seconds between bot launches
            
        Raises:
            Exception: If any bot fails to initialize
        """
        for i in range(num_bots):
            try:
                # Create domain entity with event bus
                bot = Bot.create(self.event_bus)
                self.bots.append(bot)
                
                # Create infrastructure driver using injected factory (DIP)
                driver = self.browser_driver_factory.create(self.browser_config)
                await driver.open()
                self.drivers[str(bot.id)] = driver
                
                # Mark bot as ready (will emit BotInitializedEvent)
                bot.mark_as_ready()
                
                # Staggered delay before next bot (anti-detection)
                if i < num_bots - 1:
                    delay = random.uniform(*stagger_delay_range)
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                error_msg = f"Failed to initialize bot #{i+1}: {str(e)}"
                logger = get_logger(__name__)
                logger.error("bot_initialization_failed", bot_number=i+1, error=str(e))
                if 'bot' in locals():
                    bot.mark_as_error(error_msg)  # Will emit BotErrorEvent
                raise

    def get_available_bot(self) -> Optional[Bot]:
        """
        Get first available bot from the pool.
        
        A bot is considered available if it has READY status.
        
        Returns:
            First bot in READY status, or None if no bots available
        """
        from extraction.domain.enums.bot_status import BotStatus
        
        for bot in self.bots:
            if bot.status == BotStatus.READY:
                return bot
        return None

    def get_all_bots(self) -> List[Bot]:
        """
        Get all bots in the pool.
        
        Returns:
            List of all bot instances
        """
        return self.bots.copy()

    def get_driver(self, bot_id: str) -> Optional[BrowserDriverInterface]:
        """
        Get browser driver for a specific bot.
        
        Args:
            bot_id: Bot identifier
            
        Returns:
            Browser driver for the bot, or None if not found
        """
        return self.drivers.get(bot_id)

    async def close_all(self) -> None:
        """
        Close all bots and release resources.
        
        This method:
        1. Closes all browser drivers concurrently
        2. Marks all bots as closed (emits BotClosedEvent)
        3. Clears internal registries
        """
        close_tasks = []
        
        for bot in self.bots:
            driver = self.drivers.get(str(bot.id))
            if driver:
                close_tasks.append(driver.close())
            bot.close()  # Will emit BotClosedEvent
        
        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)
        
        self.bots.clear()
        self.drivers.clear()

    def pool_size(self) -> int:
        """
        Get the total number of bots in the pool.
        
        Returns:
            Number of bots
        """
        return len(self.bots)
