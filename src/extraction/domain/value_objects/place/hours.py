from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExtractedPlaceHour:
    day: str  # e.g. 'Monday'
    open: str  # e.g. '09:00'
    close: str  # e.g. '17:00'


@dataclass(frozen=True)
class ExtractedPlaceHours:
    hours: tuple[ExtractedPlaceHour, ...] = field(default_factory=tuple)
