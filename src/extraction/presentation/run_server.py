"""
Server launcher with Windows event loop fix for Playwright.
This script must be used to run the server on Windows.
"""
import sys
import asyncio

# CRITICAL: Set event loop policy BEFORE uvicorn imports anything
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

if __name__ == "__main__":
    import uvicorn
    
    # Note: reload=True doesn't work well with WindowsProactorEventLoopPolicy
    # For development with hot reload, manually restart the server after changes
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disabled for Windows compatibility with Playwright
        log_level="info"
    )
