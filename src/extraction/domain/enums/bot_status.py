"""Bot status enumeration"""
from enum import Enum


class BotStatus(str, Enum):
    """
    Status of a bot during its lifecycle.
    Bots are ephemeral - they only exist in memory during execution.
    """
    INITIALIZING = "initializing"    # Browser is launching
    IDLE = "idle"                    # Ready to process tasks
    PROCESSING_TASK = "processing"   # Currently extracting places
    ERROR = "error"                  # Failed with error
    CLOSED = "closed"                # Browser closed
