from __future__ import annotations

from datetime import datetime, timedelta

from ...domain.interfaces import LicenseValidator
from ...domain.value_objects import LicenseStatus


class MockLicenseValidator(LicenseValidator):
    """
    Mock implementation for testing and development.

    Accepts any license key starting with "VALID-" as valid.
    Use "EXPIRED-" prefix for expired licenses.
    Any other prefix returns invalid.

    Usage:
        validator = MockLicenseValidator()
        status = validator.validate("VALID-1234-5678")  # Returns valid
        status = validator.validate("EXPIRED-1234")     # Returns expired
        status = validator.validate("INVALID-KEY")      # Returns invalid
    """

    def validate(self, license_key: str) -> LicenseStatus:
        if license_key.startswith("VALID-"):
            return LicenseStatus(
                valid=True,
                tier="pro",
                expires_at=datetime.utcnow() + timedelta(days=30),
                max_devices=3,
                features=("export_csv", "export_excel"),
            )
        elif license_key.startswith("EXPIRED-"):
            return LicenseStatus(
                valid=True,  # Was valid, but expired
                tier="basic",
                expires_at=datetime.utcnow() - timedelta(days=1),
                max_devices=1,
                features=("export_csv",),
            )
        else:
            return LicenseStatus(valid=False)

    def activate(self, license_key: str) -> LicenseStatus:
        return self.validate(license_key)

    def deactivate(self, license_key: str) -> bool:
        return license_key.startswith("VALID-")
