"""
Task Domain Events - Events emitted by PlaceExtractionTask aggregate

These events represent state changes in task execution and data extraction.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .domain_event import DomainEvent


@dataclass
class TaskStartedEvent(DomainEvent):
    """
    Event: Task execution started.
    
    Emitted by: PlaceExtractionTask.mark_as_started()
    Interested parties: Campaign aggregate, progress tracking
    """
    task_id: str
    search_seed: str
    location: str


@dataclass
class PlaceExtractedEvent(DomainEvent):
    """
    Event: A place was successfully extracted from Google Maps.
    
    Emitted by: PlaceExtractionTask.add_place()
    Interested parties: Progress tracking, real-time analytics
    """
    task_id: str
    place_name: str
    current_progress: int  # Number of places extracted so far


@dataclass
class TaskCompletedEvent(DomainEvent):
    """
    Event: Task finished successfully with all places extracted.
    
    Emitted by: PlaceExtractionTask.mark_as_completed()
    Interested parties: 
        - Repository (save results)
        - Campaign aggregate (update progress)
        - WebSocket clients (show completion)
    """
    task_id: str
    total_places_extracted: int
    duration_seconds: Optional[float] = None


@dataclass
class TaskFailedEvent(DomainEvent):
    """
    Event: Task failed to complete.
    
    Emitted by: PlaceExtractionTask.mark_as_failed()
    Interested parties: Error tracking, retry logic, alerting
    """
    task_id: str
    error: str
    places_extracted_before_failure: int
