"""
Browser Driver Factory Interface - Port for creating browser driver instances

Following Dependency Inversion Principle, the application layer defines the interface
and infrastructure provides the implementation.
"""
from abc import ABC, abstractmethod

from .browser_driver import BrowserDriverInterface
from ...domain.value_objects.browser import BrowserDriverConfig


class BrowserDriverFactoryInterface(ABC):
    """
    Factory interface for creating browser driver instances.
    
    This allows the application layer to request browser drivers without
    depending on concrete implementations (e.g., Playwright, Selenium).
    
    Benefits:
    - Dependency Inversion Principle (SOLID)
    - Testability (easy to mock)
    - Flexibility (switch implementations)
    - Clean Architecture boundaries
    """
    
    @abstractmethod
    def create(self, config: BrowserDriverConfig) -> BrowserDriverInterface:
        """
        Create a new browser driver instance with the given configuration.
        
        Args:
            config: Browser driver configuration
            
        Returns:
            A new browser driver instance implementing BrowserDriverInterface
            
        Note:
            The created driver is NOT opened automatically. 
            Caller must call await driver.open() or use async context manager.
        """
        pass
