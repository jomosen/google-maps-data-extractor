from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LicenseStatus:
    """
    Value object representing the current license status.

    Returned by the Licensing API after validation.
    """
    valid: bool
    tier: str | None = None  # e.g., "basic", "pro", "enterprise"
    expires_at: datetime | None = None
    max_devices: int | None = None
    features: tuple[str, ...] = ()  # e.g., ("export_csv", "export_excel", "api_access")

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def is_active(self) -> bool:
        return self.valid and not self.is_expired
