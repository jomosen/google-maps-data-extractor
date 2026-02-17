"""
Playwright Browser Driver Factory - Concrete implementation

This is the infrastructure adapter that creates Playwright-based browser drivers.
It implements the port (interface) defined in the application layer.
"""
from extraction.application.interfaces import BrowserDriverFactoryInterface, BrowserDriverInterface
from extraction.domain.value_objects.browser import BrowserDriverConfig
from .playwright_driver import PlaywrightBrowserDriver


class PlaywrightBrowserDriverFactory(BrowserDriverFactoryInterface):
    """
    Factory for creating Playwright browser driver instances.
    
    This concrete implementation lives in the infrastructure layer and can be
    injected into the application layer through dependency injection.
    
    Example:
        >>> factory = PlaywrightBrowserDriverFactory()
        >>> config = BrowserDriverConfig(headless=False)
        >>> driver = factory.create(config)
        >>> async with driver:
        ...     await driver.navigate_to("https://example.com")
    """
    
    def create(self, config: BrowserDriverConfig) -> BrowserDriverInterface:
        """
        Create a new Playwright browser driver instance.
        
        Args:
            config: Browser driver configuration
            
        Returns:
            A new PlaywrightBrowserDriver instance
        """
        return PlaywrightBrowserDriver(config)
