"""
Browser Element Finder Interface - Element location operations only
"""
from abc import ABC, abstractmethod
from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class DOMElement(Protocol):
    """Type protocol for DOM elements returned by browser drivers."""
    pass


class IBrowserElementFinder(ABC):
    """
    Interface for finding DOM elements.
    Responsible only for locating elements in the page.
    """
    
    @abstractmethod
    async def get(self, selector: str) -> Optional[DOMElement]:
        """
        Retrieve a DOM element matching the given selector.
        
        Args:
            selector: CSS selector or XPath expression.
            
        Returns:
            The matching element or None if not found.
        """
        pass
    
    @abstractmethod
    async def get_parent(self, child_selector: str) -> Optional[DOMElement]:
        """
        Retrieve a parent DOM element of the first element matching the given selector.
        """
        pass
    
    @abstractmethod
    def get_parent_element(self, child_element: DOMElement) -> Optional[DOMElement]:
        """
        Retrieve the parent DOM element of the given child element.
        """
        pass

    @abstractmethod
    async def get_parents(self, child_selector: str) -> list[DOMElement]:
        """
        Retrieve parent DOM elements of all elements matching the given selector.
        """
        pass
    
    @abstractmethod
    def get_child(self, parent_element: DOMElement, child_selector: str) -> Optional[DOMElement]:
        """
        Retrieve a child DOM element within a parent element matching the given selector.
        """
        pass
    
    @abstractmethod
    def get_children(self, parent_element: DOMElement, child_selector: str) -> list[DOMElement]:
        """
        Retrieve child DOM elements within a parent element matching the given selector.
        """
        pass
    
    @abstractmethod
    async def wait_for_selector(
        self, 
        selector: str, 
        timeout: int | float = 5000,
        state: str = "visible"
    ) -> DOMElement:
        """
        Wait until the DOM element matching 'selector' appears.
        
        Args:
            selector: CSS selector for the element to wait for.
            timeout: Maximum time to wait in milliseconds.
            state: Element state to wait for ('visible', 'attached', 'hidden').
            
        Returns:
            The element once it matches the specified state.
        """
        pass
