from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserDriverConfig:

    locale: str = "en"
    headless: bool = False
    timeout: int = 60
