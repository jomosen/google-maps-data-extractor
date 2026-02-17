from __future__ import annotations

from abc import ABC, abstractmethod

from ..value_objects import LicenseStatus


class LicenseValidator(ABC):
    """
    Port for license validation.

    Implementations:
        - HttpLicenseClient: Production adapter (calls Licensing API)
        - MockLicenseValidator: For testing/development
    """

    @abstractmethod
    def validate(self, license_key: str) -> LicenseStatus:
        """
        Validate a license key against the licensing server.

        Args:
            license_key: The user's license key.

        Returns:
            LicenseStatus with validation result and metadata.
        """
        ...

    @abstractmethod
    def activate(self, license_key: str) -> LicenseStatus:
        """
        Activate a license on this machine.

        Args:
            license_key: The license key to activate.

        Returns:
            LicenseStatus after activation attempt.
        """
        ...

    @abstractmethod
    def deactivate(self, license_key: str) -> bool:
        """
        Deactivate the license from this machine.

        Args:
            license_key: The license key to deactivate.

        Returns:
            True if deactivation succeeded.
        """
        ...
