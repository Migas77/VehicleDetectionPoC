import logging
from abc import ABC, abstractmethod

from app.schemas.poc.crash_status import CrashLocation

LOG = logging.getLogger(__name__)


class CcamInterface(ABC):
    @abstractmethod
    async def send_denm(self, location: CrashLocation) -> None:
        """Send a DENM message to vehicles near the given location."""
