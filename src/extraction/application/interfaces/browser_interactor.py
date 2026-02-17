"""
Browser Interactor Interface - Element interaction operations only
"""
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class DOMElement(Protocol):
    """Type protocol for DOM elements returned by browser drivers."""
    pass


class IBrowserInteractor(ABC):
    """
    Interface for interacting with DOM elements.
    Responsible only for clicking, scrolling, and element manipulation.
    """
    
    # Click operations
    @abstractmethod
    async def click(self, selector: str) -> None:
        """
        Click a DOM element matching the given selector.
        
        Raises:
            ElementNotFoundException: If selector doesn't match any element.
            TimeoutException: If element is not clickable within timeout.
        """
        pass
    
    @abstractmethod
    async def click_element(self, element: DOMElement) -> None:
        """
        Click the given DOM element.
        
        Args:
            element: The DOM element to click.
        """
        pass
    
    # Scroll operations
    @abstractmethod
    async def scroll(self, selector: str, number_of_times: int = 10) -> bool:
        """
        Scroll the element matching 'selector' down 'number_of_times'.
        
        Returns:
            True if scrolling was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    async def scroll_element(self, element: DOMElement, number_of_times: int = 10) -> bool:
        """
        Scroll the given element down 'number_of_times'.
        """
        pass
    
    @abstractmethod
    async def scroll_to(self, selector: str) -> None:
        """
        Scroll the page to bring the element matching 'selector' into view.
        """
        pass
    
    @abstractmethod
    async def scroll_to_element(self, element: DOMElement) -> None:
        """
        Scroll the page to bring the given element into view.
        """
        pass
