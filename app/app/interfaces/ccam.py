import logging
from abc import ABC, abstractmethod

from app.schemas.ccam import ReferencePositionWithConfidence

LOG = logging.getLogger(__name__)


class CcamInterface(ABC):
    @abstractmethod
    async def send_denm(
        self, location: ReferencePositionWithConfidence, text: str
    ) -> None:
        """Send a DENM message to vehicles near the given location with the given text."""
