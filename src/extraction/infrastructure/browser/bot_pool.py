"""
Bot Pool Manager - Manages multiple independent browser instances with staggered initialization
"""
import asyncio
import random
from typing import List, Optional
from dataclasses import dataclass

from shared.logging import get_logger
from extraction.infrastructure.browser import PlaywrightBrowserDriver
from extraction.domain.value_objects.browser import BrowserDriverConfig


@dataclass
class BotInstance:
    """Represents a single bot instance with its driver."""
    bot_id: int
    driver: PlaywrightBrowserDriver
    is_active: bool = False


class BotPool:
    """
    Manages multiple independent browser instances (bots) with:
    - Unique context per bot (separate cookies, sessions, fingerprints)
    - Staggered initialization for natural behavior
    - Concurrent task execution
    """

    def __init__(
        self, 
        num_bots: int = 3,
        config: Optional[BrowserDriverConfig] = None,
        stagger_delay: tuple[float, float] = (2.0, 5.0)
    ):
        """
        Args:
            num_bots: Number of bot instances to create
            config: Browser configuration (same for all bots)
            stagger_delay: Random delay range between bot launches (min, max) in seconds
        """
        self.num_bots = num_bots
        self.config = config or BrowserDriverConfig(
            headless=False,
            timeout=30,
            locale="en-US"
        )
        self.stagger_delay = stagger_delay
        self.bots: List[BotInstance] = []

    async def initialize(self) -> None:
        """
        Initialize all bots with staggered delays.
        Each bot gets its own independent browser context.
        """
        logger = get_logger(__name__)
        logger.info("bot_pool_initializing", num_bots=self.num_bots)
        
        for bot_id in range(1, self.num_bots + 1):
            # Create independent driver instance
            driver = PlaywrightBrowserDriver(self.config)
            
            # Launch browser (each bot has separate browser instance)
            await driver.open()
            
            bot = BotInstance(bot_id=bot_id, driver=driver, is_active=True)
            self.bots.append(bot)
            
            logger.info("bot_launched", bot_id=bot_id)
            
            # Staggered delay before launching next bot (anti-pattern detection)
            if bot_id < self.num_bots:
                delay = random.uniform(*self.stagger_delay)
                logger.debug("stagger_delay", bot_id=bot_id, delay_seconds=delay)
                await asyncio.sleep(delay)
        
        logger.info("bot_pool_ready", num_bots=self.num_bots)

    async def execute_concurrent(self, task_func, *args, **kwargs):
        """
        Execute the same task concurrently across all active bots.
        
        Args:
            task_func: Async function to execute (receives bot_instance as first arg)
            *args, **kwargs: Additional arguments for task_func
            
        Example:
            async def extract_places(bot: BotInstance, city: str):
                await bot.driver.navigate_to(f"https://maps.google.com?q={city}")
                # ... extraction logic
            
            await pool.execute_concurrent(extract_places, city="Madrid")
        """
        active_bots = [bot for bot in self.bots if bot.is_active]
        
        tasks = [
            task_func(bot, *args, **kwargs) 
            for bot in active_bots
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def execute_distributed(self, tasks: List[any], task_func):
        """
        Distribute different tasks across available bots.
        
        Args:
            tasks: List of task parameters (one per task)
            task_func: Async function (bot_instance, task_param)
            
        Example:
            cities = ["Madrid", "Barcelona", "Valencia"]
            
            async def extract_city(bot: BotInstance, city: str):
                await bot.driver.navigate_to(f"https://maps.google.com?q={city}")
            
            await pool.execute_distributed(cities, extract_city)
        """
        active_bots = [bot for bot in self.bots if bot.is_active]
        
        # Distribute tasks round-robin across bots
        task_assignments = []
        for idx, task in enumerate(tasks):
            bot = active_bots[idx % len(active_bots)]
            task_assignments.append(task_func(bot, task))
        
        results = await asyncio.gather(*task_assignments, return_exceptions=True)
        return results

    async def close_all(self) -> None:
        """Close all bot instances and release resources."""
        logger = get_logger(__name__)
        logger.info("bot_pool_closing", num_bots=len(self.bots))
        
        close_tasks = [bot.driver.close() for bot in self.bots]
        await asyncio.gather(*close_tasks, return_exceptions=True)
        
        self.bots.clear()
        logger.info("bot_pool_closed")

    async def __aenter__(self):
        """Context manager support."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on exit."""
        await self.close_all()

    def get_bot(self, bot_id: int) -> Optional[BotInstance]:
        """Get specific bot by ID."""
        for bot in self.bots:
            if bot.bot_id == bot_id:
                return bot
        return None


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

async def example_concurrent_extraction():
    """
    Example: All bots extract from the same URL concurrently.
    Use case: Extracting different pages of results from same search.
    """
    async def extract_task(bot: BotInstance, url: str):
        print(f"[Bot #{bot.bot_id}] Navigating to {url}")
        await bot.driver.navigate_to(url)
        
        # Simulate extraction work
        await asyncio.sleep(random.uniform(1, 3))
        
        # Each bot has independent session/cookies
        page_url = bot.driver.get_page_url()
        print(f"[Bot #{bot.bot_id}] Current URL: {page_url}")
        
        return f"Bot {bot.bot_id} completed"
    
    # Use context manager for automatic cleanup
    async with BotPool(num_bots=3, stagger_delay=(2, 4)) as pool:
        results = await pool.execute_concurrent(
            extract_task, 
            url="https://www.google.com"
        )
        print(f"Results: {results}")


async def example_distributed_extraction():
    """
    Example: Distribute different cities across available bots.
    Use case: Each bot extracts different geographic location.
    """
    async def extract_city(bot: BotInstance, city: str):
        print(f"[Bot #{bot.bot_id}] Extracting places in {city}")
        
        search_url = f"https://www.google.com/maps/search/restaurants+{city}"
        await bot.driver.navigate_to(search_url)
        
        # Simulate extraction
        await asyncio.sleep(random.uniform(2, 5))
        
        # Take screenshot for monitoring
        await bot.driver.take_screenshot(
            path=f"screenshots/bot_{bot.bot_id}_{city}.png"
        )
        
        return {
            "bot_id": bot.bot_id,
            "city": city,
            "places_found": random.randint(10, 50)
        }
    
    cities = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao"]
    
    async with BotPool(num_bots=3, stagger_delay=(3, 6)) as pool:
        # 5 cities distributed across 3 bots (round-robin)
        # Bot 1: Madrid, Sevilla
        # Bot 2: Barcelona, Bilbao  
        # Bot 3: Valencia
        results = await pool.execute_distributed(cities, extract_city)
        
        for result in results:
            if isinstance(result, dict):
                print(f"✅ Bot #{result['bot_id']}: {result['city']} - {result['places_found']} places")


async def example_independent_contexts():
    """
    Demonstrate that each bot has completely independent context.
    Each can have different cookies, sessions, viewport sizes, etc.
    """
    config = BrowserDriverConfig(headless=False, timeout=30, locale="en-US")
    
    async with BotPool(num_bots=2, config=config, stagger_delay=(3, 5)) as pool:
        bot1 = pool.get_bot(1)
        bot2 = pool.get_bot(2)
        
        # Bot 1: Navigate to Google
        await bot1.driver.navigate_to("https://www.google.com")
        print(f"Bot 1 URL: {bot1.driver.get_page_url()}")
        
        # Bot 2: Navigate to different site (independent session)
        await bot2.driver.navigate_to("https://www.bing.com")
        print(f"Bot 2 URL: {bot2.driver.get_page_url()}")
        
        # Both browsers are open simultaneously with different sessions
        await asyncio.sleep(5)
        
        # They maintain separate cookies/state
        print("✅ Each bot has independent browser context")


if __name__ == "__main__":
    # Run examples
    print("=== Example 1: Concurrent Extraction ===")
    asyncio.run(example_concurrent_extraction())
    
    print("\n=== Example 2: Distributed Extraction ===")
    asyncio.run(example_distributed_extraction())
    
    print("\n=== Example 3: Independent Contexts ===")
    asyncio.run(example_independent_contexts())
