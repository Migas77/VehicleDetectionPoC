import asyncio
import logging
from abc import ABC, abstractmethod

from app.schemas.poc.crash_status import CrashStatusEvent

LOG = logging.getLogger(__name__)


class CrashStatusBrokerInterface(ABC):
    @abstractmethod
    def subscribe(self) -> asyncio.Queue[CrashStatusEvent]:
        """Register a new subscriber queue and return it."""

    @abstractmethod
    def unsubscribe(self, queue: asyncio.Queue[CrashStatusEvent]) -> None:
        """Remove a subscriber queue (called on WebSocket disconnect)."""

    @abstractmethod
    def publish(self, event: CrashStatusEvent) -> None:
        """Fan out a status event to all currently connected WebSocket clients."""
