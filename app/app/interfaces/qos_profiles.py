import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from app.schemas.poc.ue_with_qos import UeWithQoS

LOG = logging.getLogger(__name__)


class QoSProfilesInterface(ABC):
    @abstractmethod
    async def get_qos_profiles(
        self, ue: Optional[UeWithQoS] = None
    ) -> list[dict[str, Any]]:
        """Return QoS profiles from the network.

        If `ue` is provided, fetches only the profile matching the UE's expected
        qos_profile_name. Otherwise, returns all available profiles.
        """

    @abstractmethod
    async def verify_qos_profile(self, ue: UeWithQoS) -> bool:
        """Verify the QoS profile exists in the network and matches the configured QosProfile.

        Returns True if found, False otherwise (or if it doesn't match network requirements).
        """
