"""
Base Domain Event - Abstract base for all domain events

Domain events represent something that happened in the domain that domain
experts care about. They are always named in past tense.
"""
from dataclasses import dataclass
from datetime import datetime
from abc import ABC


@dataclass
class DomainEvent(ABC):
    """
    Base class for all domain events.
    
    Domain events are immutable records of something that happened.
    They should contain all information needed for interested parties to react.
    
    Attributes:
        occurred_at: When the event occurred
        aggregate_id: ID of the aggregate that emitted this event
    """
    occurred_at: datetime
    aggregate_id: str
    
    def __post_init__(self):
        """Ensure occurred_at is set"""
        if not self.occurred_at:
            object.__setattr__(self, 'occurred_at', datetime.now())
