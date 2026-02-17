"""
Browser Navigator Interface - Navigation operations only
"""
from abc import ABC, abstractmethod


class IBrowserNavigator(ABC):
    """
    Interface for browser navigation operations.
    Responsible only for URL navigation and page state.
    """
    
    @abstractmethod
    async def navigate_to(self, url: str) -> None:
        """Navigate to a given URL."""
        pass
    
    @abstractmethod
    def get_page_url(self) -> str:
        """Return the current page URL as a string."""
        pass
    
    @abstractmethod
    async def get_page_content(self) -> str:
        """
        Return the current page HTML content as a string.
        Useful for parsers, extractors and debugging.
        """
        pass
