import logging
from abc import ABC, abstractmethod
from typing import Any

from app.schemas.poc import UE
from app.schemas.poc.ue_with_qos import UeWithQoS

LOG = logging.getLogger(__name__)


class QoDProvisioningInterface(ABC):
    @abstractmethod
    async def assign_qos_profile(self, ue: UeWithQoS) -> str:
        """Create an indefinite QoS provisioning for the UE and return its provisioning ID."""

    @abstractmethod
    async def get_qod_provisioning(self, provisioning_id: str) -> dict[str, Any]:
        """Retrieve the QoS provisioning info by ID."""

    @abstractmethod
    async def delete_qod_provisioning(self, provisioning_id: str) -> bool:
        """Delete the QoS provisioning by ID. Returns True on success."""

    @abstractmethod
    async def retrieve_qod_provisioning_by_device(self, ue: UE) -> str | None:
        """Find the provisioning ID for the given UE device. Returns None if not found."""
