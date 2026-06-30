import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime

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
    async def publish(self, event: CrashStatusEvent) -> None:
        """Persist the event to Redis and fan out to all currently connected WebSocket clients."""

    @abstractmethod
    async def list_events(
        self, before: datetime | None, offset: int, limit: int
    ) -> list[CrashStatusEvent]:
        """Return crash status events, most-recent first, with timestamp strictly before `before` (or all if None)."""

    @abstractmethod
    async def get_incident(self, incident_id: str) -> list[CrashStatusEvent]:
        """Return all events recorded for a given incident, in chronological order."""
