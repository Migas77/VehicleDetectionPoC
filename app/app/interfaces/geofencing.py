import logging
from abc import ABC, abstractmethod
from typing import cast

from app.redis import get_redis
from app.schemas.poc.area import SurveyedArea
from app.schemas.poc.ue import UE

LOG = logging.getLogger(__name__)


class GeofencingInterface(ABC):
    def __init__(self) -> None:
        self._redis = get_redis()

    @staticmethod
    def subscription_key(ue_supi: str, subscription_id: str) -> str:
        """Build the Redis key under which a UE's geofencing subscription is stored."""
        return f"poc_geofencing_{ue_supi}_{subscription_id}"

    @staticmethod
    def crash_subscribers_key(camera_supi: str) -> str:
        """Build the Redis key for the set of pedestrians currently inside a camera's area."""
        return f"poc_camera_crash_subscribers_{camera_supi}"

    @abstractmethod
    async def create_geofencing_subscription(
        self, ue: UE, area: SurveyedArea
    ) -> list[str]:
        """Subscribe to area-entered/area-left for the UE in the given area.

        Returns the created subscription IDs (two for CAMARA, one for NEF).
        """

    @abstractmethod
    async def delete_geofencing_subscription(
        self, ue: UE, subscription_id: str
    ) -> bool:
        """Delete a geofencing subscription by ID. Returns True on success."""

    async def update_geofencing_subscription(
        self, ue: UE, area: SurveyedArea, subscription_ids: list[str]
    ) -> list[str]:
        """Recreate the subscription for a new area, then delete the old one(s).

        CAMARA geofencing has no update endpoint, so we always create before deleting.
        Returns the new subscription IDs.
        """
        new_ids = await self.create_geofencing_subscription(ue, area)
        for subscription_id in subscription_ids:
            await self.delete_geofencing_subscription(ue, subscription_id)
        return new_ids

    async def get_geofencing_subscription(
        self, ue: UE, subscription_id: str
    ) -> str | None:
        """Return the stored value for a geofencing subscription, or None if absent."""
        result = await self._redis.get(self.subscription_key(ue.supi, subscription_id))
        return cast("str | None", result)

    async def get_all_geofencing_subscriptions(self, ue: UE) -> list[str]:
        """Return all stored geofencing subscription ids for the given UE."""
        prefix = f"poc_geofencing_{ue.supi}_"
        keys = await self._redis.keys(f"{prefix}*")
        # the subscription id is the key suffix (the stored value differs per backend)
        return [cast(str, key)[len(prefix) :] for key in keys]

    async def register_in_camera_area(self, camera_supi: str, ue_supi: str) -> None:
        """Record that a pedestrian UE entered a camera's area (crash-notification set)."""
        await self._redis.sadd(self.crash_subscribers_key(camera_supi), ue_supi)

    async def unregister_from_camera_area(self, camera_supi: str, ue_supi: str) -> None:
        """Record that a pedestrian UE left a camera's area."""
        await self._redis.srem(self.crash_subscribers_key(camera_supi), ue_supi)

    async def get_camera_area_subscribers(self, camera_supi: str) -> set[str]:
        """Return the pedestrian UE supis currently inside a camera's area."""
        result = await self._redis.smembers(self.crash_subscribers_key(camera_supi))
        return cast("set[str]", result)

    async def clear_camera_area_subscribers(self, camera_supi: str) -> None:
        """Clear the set of pedestrians inside a camera's area."""
        await self._redis.delete(self.crash_subscribers_key(camera_supi))
