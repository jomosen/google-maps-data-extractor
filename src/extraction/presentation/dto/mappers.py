"""
Mappers - Convert between Domain Models and Presentation DTOs

These mappers implement the Anti-Corruption Layer pattern,
translating between internal domain models and external representations.
"""
import base64
from extraction.domain.value_objects.bot_snapshot import BotSnapshot
from extraction.presentation.dto.bot_snapshot_dto import BotSnapshotDTO


def bot_snapshot_to_dto(snapshot: BotSnapshot) -> BotSnapshotDTO:
    """
    Convert domain BotSnapshot to presentation BotSnapshotDTO.
    
    Transformations applied:
    - BotStatus enum → string value
    - bytes screenshot → base64 string
    - Domain structure → presentation structure
    
    Args:
        snapshot: Domain bot snapshot with raw bytes
        
    Returns:
        DTO suitable for WebSocket/JSON serialization
    """
    return BotSnapshotDTO(
        bot_id=snapshot.bot_id,
        status=snapshot.status.value,  # Enum → string
        screenshot=base64.b64encode(snapshot.screenshot_bytes).decode('utf-8'),  # bytes → base64
        current_url=snapshot.current_url,
        task_id=snapshot.current_task_id
    )
