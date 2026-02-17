"""
Presentation Layer DTOs (Data Transfer Objects)

DTOs are used to transfer data between layers, specifically from domain to presentation.
They decouple domain models from external representations (JSON, WebSocket, REST API).
"""
from .bot_snapshot_dto import BotSnapshotDTO
from .mappers import bot_snapshot_to_dto

__all__ = [
    "BotSnapshotDTO",
    "bot_snapshot_to_dto",
]
