"""
Playwright implementation of BrowserDriverInterface with stealth capabilities.
"""
import os
import asyncio
import time
import random
from typing import Optional

from playwright.async_api import async_playwright, Page, ElementHandle, TimeoutError as PlaywrightTimeoutError

try:
    from playwright_stealth import stealth_async
except ImportError:
    # Fallback if stealth_async not available
    async def stealth_async(page):
        """Fallback stealth implementation."""
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

from extraction.application.interfaces import BrowserDriverInterface, DOMElement
from extraction.domain.value_objects.browser import BrowserDriverConfig


WAIT_TIMEOUT = 10000  # milliseconds
SCROLL_PAUSE_TIME = 1.0  # seconds - pause between scrolls to simulate human behavior
CLICK_DELAY_MIN = 2.0  # seconds - minimum delay after clicks
CLICK_DELAY_MAX = 3.0  # seconds - maximum delay after clicks


class PlaywrightBrowserDriver(BrowserDriverInterface):
    """
    Async Playwright implementation with stealth mode for undetected scraping.
    
    Features:
    - Async/await for non-blocking operations
    - Stealth mode to bypass bot detection
    - Random delays to simulate human behavior
    - Context manager support for automatic cleanup
    """

    def __init__(self, config: BrowserDriverConfig):
        self._config = config
        self._playwright = None
        self.browser = None
        self.context = None
        self.page: Optional[Page] = None

    @property
    def config(self) -> BrowserDriverConfig:
        return self._config

    # =========================================================================
    # Browser Lifecycle
    # =========================================================================

    async def open(self) -> None:
        """Launch browser with stealth configuration."""
        self._playwright = await async_playwright().start()

        self.browser = await self._playwright.chromium.launch(
            headless=self.config.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-dev-shm-usage",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-popup-blocking",
                "--disable-extensions",
                "--disable-component-extensions-with-background-pages",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
                "--enable-features=NetworkService,NetworkServiceInProcess",
                "--force-color-profile=srgb",
                "--metrics-recording-only",
                "--mute-audio",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-site-isolation-trials"
            ],
            timeout=self.config.timeout * 1000
        )

        context_args = {
            "locale": self.config.locale,
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        self.context = await self.browser.new_context(**context_args)
        self.page = await self.context.new_page()

        # Apply stealth mode asynchronously
        await stealth_async(self.page)
        
        # Additional stealth: Override navigator properties
        await self.page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override plugins to avoid detection
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Chrome runtime
            window.chrome = {
                runtime: {}
            };
            
            // Permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        # Random delay to simulate human behavior (0-3s like working implementation)
        await asyncio.sleep(random.uniform(0, 3))

    async def close(self) -> None:
        """Close browser and release all resources."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()

    # =========================================================================
    # Navigation (IBrowserNavigator)
    # =========================================================================

    async def navigate_to(self, url: str) -> None:
        """Navigate to a given URL."""
        await self.page.goto(url, timeout=self.config.timeout * 1000)

    def get_page_url(self) -> str:
        """Return the current page URL as a string."""
        return self.page.url

    async def get_page_content(self) -> str:
        """Return the current page HTML content as a string."""
        return await self.page.content()

    # =========================================================================
    # Element Finding (IBrowserElementFinder)
    # =========================================================================

    async def get(self, selector: str) -> Optional[DOMElement]:
        """Retrieve a DOM element matching the given selector."""
        try:
            element = await self.page.query_selector(selector)
            return element
        except PlaywrightTimeoutError:
            return None

    async def get_parent(self, child_selector: str) -> Optional[DOMElement]:
        """Retrieve a parent DOM element of the first element matching the given selector."""
        child_elements = await self.page.query_selector_all(child_selector)
        if child_elements:
            parent = await child_elements[0].evaluate_handle("el => el.parentElement")
            return parent.as_element()
        return None

    def get_parent_element(self, child_element: DOMElement) -> Optional[DOMElement]:
        """Retrieve the parent DOM element of the given child element."""
        # Note: This is sync because evaluate_handle returns immediately with a handle
        parent = child_element.evaluate_handle("el => el.parentElement")
        return parent.as_element()

    async def get_parents(self, child_selector: str) -> list[DOMElement]:
        """Retrieve parent DOM elements of all elements matching the given selector."""
        child_elements = await self.page.query_selector_all(child_selector)
        parent_elements = []
        for el in child_elements:
            parent = await el.evaluate_handle("el => el.parentElement")
            parent_elements.append(parent.as_element())
        return parent_elements

    def get_child(self, parent_element: DOMElement, child_selector: str) -> Optional[DOMElement]:
        """Retrieve a child DOM element within a parent element matching the given selector."""
        return parent_element.query_selector(child_selector)

    def get_children(self, parent_element: DOMElement, child_selector: str) -> list[DOMElement]:
        """Retrieve child DOM elements within a parent element matching the given selector."""
        return parent_element.query_selector_all(child_selector)

    async def wait_for_selector(
        self, 
        selector: str, 
        timeout: int | float = 5000,
        state: str = "visible"
    ) -> DOMElement:
        """
        Wait until the DOM element matching 'selector' appears.
        
        Returns the element once it matches the specified state.
        """
        element = await self.page.wait_for_selector(
            selector, 
            timeout=timeout,
            state=state
        )
        return element

    # =========================================================================
    # Interaction (IBrowserInteractor)
    # =========================================================================

    async def click(self, selector: str) -> None:
        """Click a DOM element matching the given selector."""
        await self.page.click(selector)
        # Delay after click to simulate human behavior (2-3s like working implementation)
        await asyncio.sleep(random.uniform(CLICK_DELAY_MIN, CLICK_DELAY_MAX))

    async def click_element(self, element: DOMElement) -> None:
        """Click the given DOM element."""
        await element.click()
        await asyncio.sleep(random.uniform(2, 3))

    async def scroll(self, selector: str, number_of_times: int = 10) -> bool:
        """Scroll the element matching 'selector' down 'number_of_times'."""
        element = await self.page.query_selector(selector)
        if not element:
            return False

        return await self.scroll_element(element, number_of_times)

    async def scroll_element(self, element: DOMElement, number_of_times: int = 10) -> bool:
        """Scroll the given element down 'number_of_times'."""
        if not element:
            return False

        can_scroll_further = True
        previous_scroll_height = await element.evaluate("(el) => el.scrollHeight")
        i = 0

        while can_scroll_further and i < number_of_times:
            await element.evaluate("(el) => { el.scrollTop = el.scrollHeight }")
            await asyncio.sleep(SCROLL_PAUSE_TIME)

            new_scroll_height = await element.evaluate("(el) => el.scrollHeight")
            if new_scroll_height == previous_scroll_height:
                can_scroll_further = False

            previous_scroll_height = new_scroll_height
            i += 1

        return can_scroll_further

    async def scroll_to(self, selector: str) -> None:
        """Scroll the page to bring the element matching 'selector' into view."""
        element = await self.page.query_selector(selector)
        await self.scroll_to_element(element)

    async def scroll_to_element(self, element: DOMElement) -> None:
        """Scroll the page to bring the given element into view."""
        if element:
            await self.page.evaluate("(el) => el.scrollIntoView({block: 'center'})", element)

    # =========================================================================
    # Content Extraction (IBrowserContentExtractor)
    # =========================================================================

    def get_element_text_content(self, element: DOMElement) -> str:
        """Get the text content of the given DOM element (including hidden text)."""
        if element:
            text = element.text_content()
            return text.strip() if text else ""
        return ""

    def get_element_inner_text(self, element: DOMElement) -> str:
        """Get the inner text content of the given DOM element (only visible text)."""
        if element:
            inner_text = element.evaluate("el => el.innerText")
            return str(inner_text).strip() if inner_text else ""
        return ""

    def get_child_text(self, parent_element: DOMElement, child_selector: str) -> str:
        """Get the text content of a child element within a parent element."""
        child = parent_element.query_selector(child_selector)
        if child:
            text = child.inner_text()
            return text.strip() if text else ""
        return ""

    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get the attribute value of an element matching the selector."""
        element = self.page.query_selector(selector)
        return self.get_element_attribute(element, attribute)

    def get_element_attribute(self, element: DOMElement, attribute: str) -> Optional[str]:
        """Get the attribute value of the given DOM element."""
        if element:
            return element.get_attribute(attribute)
        return None

    def get_child_attribute(
        self, 
        parent_element: DOMElement, 
        child_selector: str, 
        attribute: str
    ) -> Optional[str]:
        """Get the attribute value of a child element within a parent element."""
        child = parent_element.query_selector(child_selector)
        if child:
            return child.get_attribute(attribute)
        return None

    async def evaluate(self, script: str) -> any:
        """Evaluate a JavaScript script in the browser page context."""
        return await self.page.evaluate(script)

    # =========================================================================
    # Screenshots (IBrowserScreenshotter)
    # =========================================================================

    async def take_screenshot(
        self, 
        path: Optional[str] = None,
        full_page: bool = False
    ) -> bytes:
        """
        Take a screenshot of the current page.
        
        Returns screenshot as raw bytes. If path is provided, also saves to disk.
        """
        screenshot_bytes = await self.page.screenshot(
            path=path,
            full_page=full_page
        )
        return screenshot_bytes

    # =========================================================================
    # Helper Methods (Additional Utilities)
    # =========================================================================

    async def take_page_screenshot(self, e: Exception) -> str:
        """
        Take a screenshot with auto-generated filename based on page title and exception.
        
        This is a helper method that provides the original behavior from the sync version.
        Useful for error logging and debugging.
        
        Args:
            e: The exception that triggered the screenshot.
            
        Returns:
            Path to the saved screenshot file.
            
        Raises:
            RuntimeError: If screenshot fails to save.
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")

        try:
            # Title of the page (may contain unsafe chars)
            title = await self.page.title()

            # First 50 chars of the exception
            exc_short = str(e)[:50]

            # Combine title + exception preview
            raw_name = f"{title}__{exc_short}"

            # Sanitize: allow alphanumeric + '-' + '_'
            safe_name = "".join(c for c in raw_name if c.isalnum() or c in "-_")

            # Trim if too long
            safe_name = safe_name[:80]

            filename = f"{timestamp}_{safe_name}.png"
            path = os.path.join("log", filename)

            # Ensure log directory exists
            os.makedirs("log", exist_ok=True)

            await self.page.screenshot(path=path)
            return path

        except Exception as nested:
            raise RuntimeError(f"Failed to take screenshot: {nested}")
