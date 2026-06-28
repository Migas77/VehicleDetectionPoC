import asyncio
import logging
from typing import cast

from app.interfaces.crash_status import CrashStatusBrokerInterface
from app.redis import get_redis
from app.schemas.poc.crash_status import CrashNotificationStatus, CrashStatusEvent

LOG = logging.getLogger(__name__)

_INCIDENTS_KEY = "poc:crash_status:incidents"
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
        async with self._redis.pipeline() as pipe:
            pipe.rpush(incident_events_key, event.model_dump_json())
            if event.status == CrashNotificationStatus.detected:
                pipe.zadd(
                    _INCIDENTS_KEY,
                    {str(event.incident_id): event.timestamp.timestamp()},
                )
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

    async def list_incidents(self, offset: int, limit: int) -> list[CrashStatusEvent]:
        incident_ids = cast(
            list[str],
            await self._redis.zrevrange(_INCIDENTS_KEY, offset, offset + limit - 1),
        )
        if not incident_ids:
            return []

        async with self._redis.pipeline() as pipe:
            for incident_id in incident_ids:
                pipe.lindex(f"{_INCIDENT_EVENTS_KEY_PREFIX}{incident_id}:events", 0)
            results: list[str | None] = await pipe.execute()

        summaries: list[CrashStatusEvent] = []
        for incident_id, detected_json in zip(incident_ids, results):
            if not isinstance(detected_json, str):
                LOG.warning(
                    "Corrupted Redis data for incident %s, skipping", incident_id
                )
                continue
            summaries.append(CrashStatusEvent.model_validate_json(detected_json))

        return summaries

    async def get_incident(self, incident_id: str) -> list[CrashStatusEvent]:
        key = f"{_INCIDENT_EVENTS_KEY_PREFIX}{incident_id}:events"
        events_json = cast(list[str], await self._redis.lrange(key, 0, -1))
        return [CrashStatusEvent.model_validate_json(e) for e in events_json]
