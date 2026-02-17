from __future__ import annotations

import hashlib
import platform
import uuid

from ...domain.interfaces import LicenseValidator
from ...domain.value_objects import LicenseStatus


def _generate_machine_id() -> str:
    """
    Generate a unique machine fingerprint.

    Combines hardware identifiers to create a stable machine ID.
    TODO: Implement proper fingerprinting (MAC address, disk serial, etc.)
    """
    # Placeholder implementation
    raw = f"{platform.node()}-{platform.machine()}-{uuid.getnode()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


class HttpLicenseClient(LicenseValidator):
    """
    HTTP adapter for the Licensing API.

    Communicates with the licensing microservice on the VPS
    to validate, activate, and deactivate licenses.

    Usage:
        client = HttpLicenseClient(base_url="https://api.myapp.com")
        status = client.validate("LICENSE-KEY-HERE")
        if status.is_active:
            # Allow app usage
            pass
    """

    def __init__(self, base_url: str, machine_id: str | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._machine_id = machine_id or _generate_machine_id()

    def validate(self, license_key: str) -> LicenseStatus:
        """
        Validate license against the licensing server.

        POST /api/license/validate
        {
            "license_key": "...",
            "machine_id": "..."
        }

        TODO: Implement HTTP call with requests library.
        TODO: Handle network errors with grace period (offline mode).
        TODO: Cache valid responses locally for offline resilience.
        """
        raise NotImplementedError("TODO: Implement HTTP validation")

    def activate(self, license_key: str) -> LicenseStatus:
        """
        Activate license on this machine.

        POST /api/license/activate
        {
            "license_key": "...",
            "machine_id": "...",
            "machine_name": "..."  # Optional, for user's device list
        }

        TODO: Implement HTTP call.
        TODO: Store activation locally for offline validation.
        """
        raise NotImplementedError("TODO: Implement HTTP activation")

    def deactivate(self, license_key: str) -> bool:
        """
        Deactivate license from this machine.

        POST /api/license/deactivate
        {
            "license_key": "...",
            "machine_id": "..."
        }

        TODO: Implement HTTP call.
        TODO: Clear local activation cache.
        """
        raise NotImplementedError("TODO: Implement HTTP deactivation")
