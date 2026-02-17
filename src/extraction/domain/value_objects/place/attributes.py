from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExtractedPlaceAttributes:
    attributes: list[str] = field(default_factory=list)
