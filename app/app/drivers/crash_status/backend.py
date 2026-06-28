import asyncio
import logging

from app.interfaces.crash_status import CrashStatusBrokerInterface
from app.schemas.poc.crash_status import CrashStatusEvent

LOG = logging.getLogger(__name__)


class AsyncioCrashStatusBroker(CrashStatusBrokerInterface):
    """In-process pub/sub broker for crash notification status events.

    Each WebSocket connection subscribes its own asyncio.Queue; the crash-inference
    background task publishes events to all active queues via put_nowait (never blocks).
    """

    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[CrashStatusEvent]] = set()

    def subscribe(self) -> asyncio.Queue[CrashStatusEvent]:
        queue: asyncio.Queue[CrashStatusEvent] = asyncio.Queue()
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[CrashStatusEvent]) -> None:
        self._subscribers.discard(queue)

    def publish(self, event: CrashStatusEvent) -> None:
        for queue in self._subscribers:
            queue.put_nowait(event)
        LOG.debug(
            "Published crash status event: incident=%s status=%s channel=%s recipient=%s to %d subscriber(s)",
            event.incident_id,
            event.status,
            event.channel,
            event.recipient,
            len(self._subscribers),
        )
