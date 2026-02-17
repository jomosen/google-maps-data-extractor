from __future__ import annotations

from dataclasses import dataclass

from ulid import ULID


def _validate_ulid(value: str) -> None:
    try:
        ULID.from_str(value)
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError(f"Invalid ULID: {value}") from exc


@dataclass(frozen=True)
class CampaignId:
    value: str

    def __post_init__(self) -> None:
        _validate_ulid(self.value)

    @staticmethod
    def new() -> "CampaignId":
        return CampaignId(str(ULID()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ExtractionTaskId:
    value: str

    def __post_init__(self) -> None:
        _validate_ulid(self.value)

    @staticmethod
    def new() -> "ExtractionTaskId":
        return ExtractionTaskId(str(ULID()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class BotId:
    value: str

    def __post_init__(self) -> None:
        _validate_ulid(self.value)

    @staticmethod
    def new() -> "BotId":
        return BotId(str(ULID()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class EnrichmentTaskId:
    value: str

    def __post_init__(self) -> None:
        _validate_ulid(self.value)

    @staticmethod
    def new() -> "EnrichmentTaskId":
        return EnrichmentTaskId(str(ULID()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ReviewId:
    value: str

    def __post_init__(self) -> None:
        _validate_ulid(self.value)

    @staticmethod
    def new() -> "ReviewId":
        return ReviewId(str(ULID()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PlaceId:
    """
    Identificador externo del place (ej: Google Place ID).
    No se asume ULID.
    """
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PlaceId must be a non-empty string")

    def __str__(self) -> str:
        return self.value
