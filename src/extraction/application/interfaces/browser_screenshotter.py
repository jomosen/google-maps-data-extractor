"""
Browser Screenshotter Interface - Screenshot operations only
"""
from abc import ABC, abstractmethod
from typing import Optional


class IBrowserScreenshotter(ABC):
    """
    Interface for taking screenshots.
    Responsible only for capturing browser viewport or page content.
    """
    
    @abstractmethod
    async def take_screenshot(
        self, 
        path: Optional[str] = None,
        full_page: bool = False
    ) -> bytes:
        """
        Take a screenshot of the current page.
        
        Args:
            path: Optional file path to save the screenshot. If None, returns bytes only.
            full_page: If True, captures the entire scrollable page.
            
        Returns:
            Screenshot as raw bytes.
            
        Note:
            If path is provided, also saves the screenshot to disk.
        """
        pass
