import logging
from abc import ABC, abstractmethod
from typing import cast

from app.redis import get_redis
from app.schemas.camara.application_profiles import ApplicationProfileId
from app.schemas.poc.ue_with_qos import UeWithQoS

LOG = logging.getLogger(__name__)


class AnalyticsInterface(ABC):
    def __init__(self) -> None:
        self._redis = get_redis()

    @staticmethod
    def _subscription_key(ue_id: int, subscription_id: str) -> str:
        """Build the Redis key under which a UE's analytics subscription id is stored."""
        return f"poc_analytics_{ue_id}_{subscription_id}"

    @abstractmethod
    async def create_analytics_subscription(
        self, ue: UeWithQoS, application_profile_id: ApplicationProfileId
    ) -> str:
        """Subscribe to network analytics for the UE. Returns the subscription ID."""

    @abstractmethod
    async def delete_analytics_subscription(
        self, ue: UeWithQoS, subscription_id: str
    ) -> bool:
        """Delete an analytics subscription by ID. Returns True on success."""

    async def get_all_analytics_subscriptions(self, ue: UeWithQoS) -> list[str]:
        """Return all stored analytics subscription ids for the given UE."""
        keys = await self._redis.keys(f"poc_analytics_{ue.id}_*")
        if not keys:
            return []
        values = await self._redis.mget(keys)
        # decode_responses=True guarantees str values (if not None)
        return [cast(str, value) for value in values if value is not None]
