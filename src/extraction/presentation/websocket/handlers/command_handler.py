"""
Command Handler - Handles commands that modify extraction state

Commands follow CQRS pattern:
- They modify state
- They return minimal confirmation (success/failure)
- They trigger domain events
"""
import asyncio
from typing import Dict, Any, Optional
from fastapi import WebSocket

from shared.logging import get_logger
from extraction.application.services.bot_orchestrator import BotOrchestrator
from extraction.application.services.bot_pool_manager import BotPoolManager
from extraction.application.services.task_queue import TaskQueue
from extraction.domain.entities.place_extraction_task import PlaceExtractionTask
from extraction.domain.value_objects.geo.geoname import Geoname
from extraction.domain.value_objects.ids import CampaignId
from extraction.domain.value_objects import BrowserDriverConfig
from extraction.infrastructure.browser import PlaywrightBrowserDriverFactory
from shared.events import EventBus


class CommandHandler:
    """
    Handles commands that modify extraction state.
    
    Commands:
    - start_extraction: Initialize and start extraction process
    - pause_extraction: Pause ongoing extraction (TODO)
    - cancel_extraction: Cancel and cleanup extraction (TODO)
    
    Each command returns a result indicating success or failure.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.browser_driver_factory = PlaywrightBrowserDriverFactory()
        # Store active extractions (campaign_id -> orchestrator)
        self.active_extractions: Dict[str, BotOrchestrator] = {}
    
    async def handle_command(
        self, 
        websocket: WebSocket, 
        command: str, 
        data: Dict[str, Any],
        event_bus: EventBus,
        blocking: bool = False  # For legacy auto-start mode
    ) -> Dict[str, Any]:
        """
        Route command to appropriate handler.
        
        Args:
            websocket: Active WebSocket connection
            command: Command name (start_extraction, pause_extraction, etc.)
            data: Command payload
            event_bus: Event bus for domain events
            
        Returns:
            Result dictionary with success status and data
        """
        self.logger.info("command_received", command=command, blocking=blocking)
        
        if command == "start_extraction":
            return await self._start_extraction(websocket, data, event_bus, blocking)
        elif command == "pause_extraction":
            return await self._pause_extraction(data)
        elif command == "cancel_extraction":
            return await self._cancel_extraction(data)
        else:
            return {
                "success": False,
                "error": f"Unknown command: {command}"
            }
    
    async def _start_extraction(
        self, 
        websocket: WebSocket, 
        data: Dict[str, Any],
        event_bus: EventBus,
        blocking: bool = False
    ) -> Dict[str, Any]:
        """
        Command: Start extraction process.
        
        Args:
            websocket: WebSocket connection
            data: Command data (campaign_id, config, etc.)
            event_bus: Event bus for domain events
            blocking: If True, waits for extraction to complete (legacy mode)
            
        Returns:
            Result with extraction_id and status
        """
        try:
            # Extract configuration from data
            # NOTE: Future improvement - receive campaign_id and load from repository
            num_bots = data.get("max_bots", data.get("num_bots", 3))
            cities = data.get("cities", [
                ("Madrid", 40.4168, -3.7038),
                ("Barcelona", 41.3851, 2.1734),
                ("Valencia", 39.4699, -0.3763)
            ])
            search_seed = data.get("search_seed", "restaurants")
            
            # Create tasks
            tasks = self._create_tasks(cities, search_seed, event_bus)
            campaign_id = str(tasks[0].campaign_id)
            
            self.logger.info(
                "extraction_command_starting",
                campaign_id=campaign_id,
                num_tasks=len(tasks),
                num_bots=num_bots
            )
            
            # Create BotPoolManager
            bot_pool_manager = BotPoolManager(
                browser_driver_factory=self.browser_driver_factory,
                event_bus=event_bus,
                browser_config=BrowserDriverConfig(
                    headless=False,
                    timeout=30,
                    locale="en-US"
                )
            )
            
            # Initialize pool with staggered delays
            await bot_pool_manager.initialize_pool(
                num_bots=num_bots,
                stagger_delay_range=(2.0, 5.0)
            )
            
            # Create TaskQueue
            task_queue = TaskQueue()
            
            # Create orchestrator
            orchestrator = BotOrchestrator(
                bot_pool_manager=bot_pool_manager,
                task_queue=task_queue
            )
            
            # Store active extraction
            self.active_extractions[campaign_id] = orchestrator
            
            if blocking:
                # Legacy mode: wait for extraction to complete
                self.logger.info("extraction_blocking_mode", campaign_id=campaign_id)
                await self._run_extraction(orchestrator, tasks, campaign_id)
            else:
                # CQRS mode: start extraction in background (non-blocking)
                asyncio.create_task(self._run_extraction(orchestrator, tasks, campaign_id))
            
            return {
                "success": True,
                "extraction_id": campaign_id,
                "num_tasks": len(tasks),
                "num_bots": num_bots,
                "message": "Extraction started successfully"
            }
            
        except Exception as e:
            self.logger.error(
                "extraction_command_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _run_extraction(
        self,
        orchestrator: BotOrchestrator,
        tasks: list,
        campaign_id: str
    ) -> None:
        """Run extraction in background."""
        try:
            await orchestrator.start_extraction(tasks=tasks)
            self.logger.info("extraction_completed", campaign_id=campaign_id)
        except Exception as e:
            self.logger.error(
                "extraction_failed",
                campaign_id=campaign_id,
                error=str(e)
            )
        finally:
            # Cleanup
            if campaign_id in self.active_extractions:
                del self.active_extractions[campaign_id]
    
    async def _pause_extraction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Command: Pause extraction (TODO - not implemented yet)."""
        extraction_id = data.get("extraction_id")
        self.logger.info("pause_command_received", extraction_id=extraction_id)
        
        # TODO: Implement pause logic
        return {
            "success": False,
            "error": "Pause not implemented yet"
        }
    
    async def _cancel_extraction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Command: Cancel extraction (TODO - not implemented yet)."""
        extraction_id = data.get("extraction_id")
        self.logger.info("cancel_command_received", extraction_id=extraction_id)
        
        # TODO: Implement cancel logic
        return {
            "success": False,
            "error": "Cancel not implemented yet"
        }
    
    def _create_tasks(
        self, 
        cities: list, 
        search_seed: str, 
        event_bus: EventBus
    ) -> list[PlaceExtractionTask]:
        """Create extraction tasks from city data."""
        tasks = []
        campaign_id = CampaignId.new()
        
        for city_name, lat, lng in cities:
            geoname = Geoname(
                geoname_id=0,
                name=city_name,
                latitude=lat,
                longitude=lng,
                country_code="ES",
                population=1000000,
                country_name="Spain"
            )
            
            task = PlaceExtractionTask.create(
                campaign_id=campaign_id,
                search_seed=search_seed,
                geoname=geoname,
                event_bus=event_bus
            )
            
            tasks.append(task)
        
        return tasks
