"""WebSocket handler for extraction streaming with auto-start"""
import asyncio
from typing import Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

from shared.logging import get_logger, bind_context, clear_context
from shared.events import EventBus
from extraction.presentation.websocket.handlers import (
    CommandHandler,
    QueryHandler,
    EventStreamHandler
)


class ExtractionWebSocketHandler:
    """
    WebSocket handler with auto-start extraction.
    
    Connects and immediately starts extraction with event streaming.
    CQRS handlers available for future extensions (pause, cancel, queries).
    """
    
    def __init__(self):
        """Initialize handler."""
        self.logger = get_logger(__name__)
        self.command_handler = CommandHandler()
        self.query_handler = QueryHandler()
        self.event_stream_handler = EventStreamHandler()

    async def handle(self, websocket: WebSocket):
        """
        Handle WebSocket connection - auto-starts extraction immediately.
        """
        await websocket.accept()
        
        # Bind WebSocket context
        client_host = websocket.client.host if websocket.client else "unknown"
        bind_context(websocket_client=client_host)
        self.logger.info("websocket_connected", client_host=client_host)
        
        # Create Event Bus
        event_bus = EventBus()
        
        try:
            # Send connection confirmation
            await websocket.send_json({
                "type": "connection",
                "message": "Connected - starting extraction",
                "status": "ready"
            })
            
            # AUTO-START extraction immediately
            await self._auto_start_extraction(websocket, event_bus)
            
        except WebSocketDisconnect:
            self.logger.info("websocket_client_disconnected")
        except Exception as e:
            self.logger.error("websocket_error", error=str(e), error_type=type(e).__name__)
            try:
                await websocket.send_json({
                    "type": "error",
                    "message": f"WebSocket error: {str(e)}"
                })
            except:
                pass
        finally:
            clear_context()
            self.logger.info("websocket_session_ended")
    
    async def _auto_start_extraction(
        self,
        websocket: WebSocket,
        event_bus: EventBus
    ) -> None:
        """
        Auto-start extraction immediately on connection.
        
        1. Start event streaming
        2. Start extraction (blocking - keeps connection alive)
        """
        self.logger.info("auto_start_extraction")
        
        # Start event streaming
        await self.event_stream_handler.start_streaming(websocket, event_bus)
        
        # Start extraction with default config (blocking)
        result = await self.command_handler.handle_command(
            websocket, 
            "start_extraction", 
            {},  # Default config
            event_bus,
            blocking=True
        )
        
        await websocket.send_json({
            "type": "extraction_complete",
            **result
        })


