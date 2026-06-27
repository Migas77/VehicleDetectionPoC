import logging
from abc import ABC, abstractmethod

from app.schemas.poc.ue import UE

LOG = logging.getLogger(__name__)


class SMSInterface(ABC):
    @abstractmethod
    async def send_sms(self, ue: UE, text: str) -> None:
        """Send an SMS to the given UE."""
