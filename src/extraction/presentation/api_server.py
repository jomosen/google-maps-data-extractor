"""FastAPI server for Extraction BC"""
import sys
import asyncio
import os
import pathlib
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from shared.logging import get_logger, configure_logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from extraction.presentation.websocket.extraction_handler import ExtractionWebSocketHandler
from extraction.presentation.api import campaign_router
from extraction.presentation.api.geonames_routes import router as geonames_router
from extraction.infrastructure.persistence import init_database

# Fix for Windows: Use ProactorEventLoop to support subprocesses (required by Playwright)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Project root: src/extraction/presentation/ → src/extraction/ → src/ → root
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_PROJECT_ROOT / 'data.db'}")

# Initialize database on startup
init_database(DATABASE_URL)


# Create FastAPI app
app = FastAPI(
    title="Google Maps Data Extractor API",
    description="Backend API for real-time extraction with browser bots",
    version="1.0.0"
)

# CORS middleware - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",  # Vite dev server
        "http://localhost:5173",  # Alternative Vite port
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create screenshots directory if it doesn't exist
SCREENSHOTS_DIR = os.path.join(os.getcwd(), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# Serve static screenshots (if using URL-based approach instead of base64)
app.mount("/screenshots", StaticFiles(directory=SCREENSHOTS_DIR), name="screenshots")

# Register API routers
app.include_router(campaign_router)
app.include_router(geonames_router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "extraction-api",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "components": {
            "websocket": "available",
            "browser_drivers": "ready"
        }
    }


@app.websocket("/ws/extraction/stream")
async def websocket_extraction_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time extraction streaming.
    
    Clients connect here to receive:
    - Bot initialization updates
    - Real-time screenshots
    - Task progress updates
    - Error notifications
    """
    handler = ExtractionWebSocketHandler()
    logger = get_logger(__name__)
    
    try:
        await handler.handle(websocket)
    except WebSocketDisconnect:
        logger.info("websocket_client_disconnected")
    except Exception as e:
        logger.error("websocket_error", error=str(e), error_type=type(e).__name__)
        await websocket.close(code=1011, reason=str(e))


if __name__ == "__main__":
    import uvicorn
    
    # Configure structured logging
    configure_logging()
    logger = get_logger(__name__)
    
    logger.info(
        "server_starting",
        server_url="http://localhost:8000",
        websocket_url="ws://localhost:8000/ws/extraction/stream",
        screenshots_url="http://localhost:8000/screenshots/"
    )
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
