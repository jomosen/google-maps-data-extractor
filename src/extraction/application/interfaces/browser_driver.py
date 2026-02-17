"""
Browser Driver Interface - Complete browser automation interface

This is a composite interface that combines all browser operation interfaces.
Implementations can inherit from this unified interface or compose the smaller ones.
Lives in application/ because it's a technical detail of HOW we extract data,
not a core domain concept.
"""
from abc import ABC, abstractmethod

from ...domain.value_objects.browser import BrowserDriverConfig
from .browser_navigator import IBrowserNavigator
from .browser_element_finder import IBrowserElementFinder
from .browser_interactor import IBrowserInteractor
from .browser_content_extractor import IBrowserContentExtractor
from .browser_screenshotter import IBrowserScreenshotter


class BrowserDriverInterface(
    IBrowserNavigator,
    IBrowserElementFinder,
    IBrowserInteractor,
    IBrowserContentExtractor,
    IBrowserScreenshotter,
    ABC
):
    """
    Complete browser driver interface combining all browser operations.
    
    Inherits from:
    - IBrowserNavigator: Navigation operations
    - IBrowserElementFinder: Element location operations
    - IBrowserInteractor: Click and scroll operations
    - IBrowserContentExtractor: Content and attribute extraction
    - IBrowserScreenshotter: Screenshot operations
    
    This interface supports async/await for non-blocking I/O operations
    and implements context manager protocol for automatic resource cleanup.
    """

    @property
    @abstractmethod
    def config(self) -> BrowserDriverConfig:
        """Get the browser driver configuration."""
        pass
    
    # Context manager support
    async def __aenter__(self) -> "BrowserDriverInterface":
        """Enter async context manager."""
        await self.open()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager and cleanup resources."""
        await self.close()
    
    # Browser lifecycle
    @abstractmethod
    async def open(self) -> None:
        """Launch the browser instance (if required by the driver)."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close browser and release resources."""
        pass

