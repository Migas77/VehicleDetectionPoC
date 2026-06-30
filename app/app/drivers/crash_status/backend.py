import asyncio
import logging
from datetime import datetime
from typing import cast

from app.interfaces.crash_status import CrashStatusBrokerInterface
from app.redis import get_redis
from app.schemas.poc.crash_status import CrashStatusEvent

LOG = logging.getLogger(__name__)

_EVENTS_KEY = "poc:crash_status:events"
_INCIDENT_EVENTS_KEY_PREFIX = "poc:crash_status:incident:"


class AsyncioCrashStatusBroker(CrashStatusBrokerInterface):
    """In-process pub/sub broker for crash notification status events.

    Each WebSocket connection subscribes its own asyncio.Queue; the crash-inference
    background task publishes events to all active queues via put_nowait (never blocks).
    Events are also persisted to Redis for historical access.
    """

    def __init__(self) -> None:
        self._redis = get_redis()
        self._subscribers: set[asyncio.Queue[CrashStatusEvent]] = set()

    def subscribe(self) -> asyncio.Queue[CrashStatusEvent]:
        queue: asyncio.Queue[CrashStatusEvent] = asyncio.Queue()
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[CrashStatusEvent]) -> None:
        self._subscribers.discard(queue)

    async def publish(self, event: CrashStatusEvent) -> None:
        incident_events_key = f"{_INCIDENT_EVENTS_KEY_PREFIX}{event.incident_id}:events"
        event_json = event.model_dump_json()
        async with self._redis.pipeline() as pipe:
            pipe.rpush(incident_events_key, event_json)
            pipe.zadd(_EVENTS_KEY, {event_json: event.timestamp.timestamp()})
            await pipe.execute()

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

    async def list_events(
        self, before: datetime | None, offset: int, limit: int
    ) -> list[CrashStatusEvent]:
        max_score = f"({before.timestamp()}" if before is not None else "+inf"
        raw = cast(
            list[str],
            await self._redis.zrevrangebyscore(
                _EVENTS_KEY, max_score, "-inf", start=offset, num=limit
            ),
        )
        events: list[CrashStatusEvent] = []
        for member in raw:
            if not isinstance(member, str):
                LOG.warning("Corrupted Redis data in %s, skipping member", _EVENTS_KEY)
                continue
            events.append(CrashStatusEvent.model_validate_json(member))
        return events

    async def get_incident(self, incident_id: str) -> list[CrashStatusEvent]:
        key = f"{_INCIDENT_EVENTS_KEY_PREFIX}{incident_id}:events"
        events_json = cast(list[str], await self._redis.lrange(key, 0, -1))
        return [CrashStatusEvent.model_validate_json(e) for e in events_json]
