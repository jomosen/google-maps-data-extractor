"""
Browser Content Extractor Interface - Content extraction operations only
"""
from abc import ABC, abstractmethod
from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class DOMElement(Protocol):
    """Type protocol for DOM elements returned by browser drivers."""
    pass


class IBrowserContentExtractor(ABC):
    """
    Interface for extracting content from DOM elements.
    Responsible only for getting text, attributes, and element content.
    """
    
    # Text extraction
    @abstractmethod
    def get_element_text_content(self, element: DOMElement) -> str:
        """
        Get the text content of the given DOM element (including hidden text).
        """
        pass
    
    @abstractmethod
    def get_element_inner_text(self, element: DOMElement) -> str:
        """
        Get the inner text content of the given DOM element (only visible text).
        """
        pass
    
    @abstractmethod
    def get_child_text(self, parent_element: DOMElement, child_selector: str) -> str:
        """
        Get the text content of a child element within a parent element.
        """
        pass
    
    # Attributes extraction
    @abstractmethod
    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """
        Get the attribute value of an element matching the selector.
        """
        pass
    
    @abstractmethod
    def get_element_attribute(self, element: DOMElement, attribute: str) -> Optional[str]:
        """
        Get the attribute value of the given DOM element.
        """
        pass
    
    @abstractmethod
    def get_child_attribute(
        self, 
        parent_element: DOMElement, 
        child_selector: str, 
        attribute: str
    ) -> Optional[str]:
        """
        Get the attribute value of a child element within a parent element.
        """
        pass
    
    # JavaScript evaluation
    @abstractmethod
    async def evaluate(self, script: str) -> any:
        """
        Evaluate a JavaScript script in the browser context.
        
        Args:
            script: The JavaScript code to execute.
            
        Returns:
            The result of the script execution.
        """
        pass
