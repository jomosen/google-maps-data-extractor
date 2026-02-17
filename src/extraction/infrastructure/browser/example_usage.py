"""
Example usage of PlaywrightBrowserDriver with async/await
"""
import asyncio
from extraction.infrastructure.browser import PlaywrightBrowserDriver
from extraction.domain.value_objects.browser import BrowserDriverConfig


async def example_usage():
    """Demonstrate async browser automation with stealth mode."""
    
    # Create configuration
    config = BrowserDriverConfig(
        headless=False,  # Set to True for headless mode
        timeout=30,
        locale="en-US"
    )
    
    # Use context manager for automatic cleanup
    async with PlaywrightBrowserDriver(config) as driver:
        # Navigate to a page
        await driver.navigate_to("https://www.google.com")
        
        # Wait for search box
        search_box = await driver.wait_for_selector('textarea[name="q"]')
        
        # Click and type (if needed)
        await driver.click('textarea[name="q"]')
        
        # Get page info
        url = driver.get_page_url()
        print(f"Current URL: {url}")
        
        # Take screenshot
        screenshot_bytes = await driver.take_screenshot(
            path="example_screenshot.png",
            full_page=False
        )
        print(f"Screenshot taken: {len(screenshot_bytes)} bytes")
        
        # Find elements
        element = await driver.get('textarea[name="q"]')
        if element:
            text = driver.get_element_attribute(element, "name")
            print(f"Element attribute: {text}")
        
        # Scroll example
        body = await driver.get("body")
        if body:
            await driver.scroll_element(body, number_of_times=3)
        
        # Evaluate JavaScript
        title = await driver.evaluate("document.title")
        print(f"Page title: {title}")


async def error_handling_example():
    """Example with error screenshot."""
    config = BrowserDriverConfig(headless=False, timeout=30, locale="en-US")
    
    driver = PlaywrightBrowserDriver(config)
    await driver.open()
    
    try:
        await driver.navigate_to("https://example.com")
        # ... do something that might fail
        raise ValueError("Example error for screenshot")
        
    except Exception as e:
        # Take screenshot with auto-generated name
        screenshot_path = await driver.take_page_screenshot(e)
        print(f"Error screenshot saved: {screenshot_path}")
        
    finally:
        await driver.close()


if __name__ == "__main__":
    # Run the async example
    asyncio.run(example_usage())
    
    # Or with error handling
    # asyncio.run(error_handling_example())
