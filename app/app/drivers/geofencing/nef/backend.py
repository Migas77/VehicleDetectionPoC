import logging
from datetime import datetime, timezone
from functools import cached_property
from ipaddress import IPv4Address
from uuid import uuid4

import httpx
from pydantic import AnyUrl

from app.interfaces.geofencing import GeofencingInterface
from app.schemas.camara.geofencing import SubscriptionEventType
from app.schemas.nef.monitoringevent import (
    MonitoringEventSubscription,
    MonitoringType,
)
from app.schemas.poc.area import SurveyedArea
from app.schemas.poc.geofencing import ManagedGeofencingSubscription
from app.schemas.poc.ue import UE
from app.settings import settings

LOG = logging.getLogger(__name__)

# The NEF-managed subscription emits both transitions; computed in the callback
_GEOFENCING_EVENT_TYPES = [
    SubscriptionEventType.v0_area_entered,
    SubscriptionEventType.v0_area_left,
]
# Far-future expiry — geofencing subscriptions live until explicit deletion
_MONITOR_EXPIRE_TIME = datetime(9999, 12, 31, 23, 59, 59, tzinfo=timezone.utc)


class NefGeofencingBackend(GeofencingInterface):
    """Manages geofencing via NEF MonitoringEvent LOCATION_REPORTING subscriptions.

    NEF exposes no geofencing primitive, so the enter/leave logic is computed in the
    callback and the whole managed subscription object is stored in Redis.
    """

    @cached_property
    def _client(self) -> httpx.AsyncClient:
        return settings.create_nef_auth_client()

    async def create_geofencing_subscription(
        self, ue: UE, area: SurveyedArea
    ) -> list[str]:
        managed_id = str(uuid4())
        notification_url = (
            f"{str(settings.nef.poc_notification_url).rstrip('/')}"
            f"/callbacks/geofencing/nef/{ue.id}/{area.camera_id}/{managed_id}"
        )
        if ue.msisdn is not None:
            payload = MonitoringEventSubscription(
                monitoringType=MonitoringType.LOCATION_REPORTING,
                notificationDestination=AnyUrl(notification_url),
                monitorExpireTime=_MONITOR_EXPIRE_TIME,
                immediateRep=True,
                msisdn=ue.msisdn,
            )
        elif ue.ip_address_v4 is not None:
            payload = MonitoringEventSubscription(
                monitoringType=MonitoringType.LOCATION_REPORTING,
                notificationDestination=AnyUrl(notification_url),
                monitorExpireTime=_MONITOR_EXPIRE_TIME,
                immediateRep=True,
                ipv4Addr=IPv4Address(ue.ip_address_v4),
            )
        else:
            raise ValueError(
                f"Cannot identify UE id={ue.id} for NEF geofencing: "
                "neither msisdn nor ip_address_v4 is set"
            )

        url = f"/nef/api/v1/3gpp-monitoring-event/v1/{settings.poc_af_id}/subscriptions"
        LOG.info(
            "Creating NEF geofencing (location) subscription for UE id=%s, camera id=%s",
            ue.id,
            area.camera_id,
        )
        res = await self._client.post(
            url,
            content=payload.model_dump_json(exclude_none=True),
            headers={"Content-Type": "application/json"},
        )
        if not res.is_success:
            raise RuntimeError(
                f"NEF geofencing subscription failed ({res.status_code}): {res.text}"
            )
        subscription = MonitoringEventSubscription.model_validate_json(res.content)
        if subscription.self is None:
            raise RuntimeError(
                f"NEF geofencing subscription response missing 'self' link for UE id={ue.id}"
            )
        managed = ManagedGeofencingSubscription(
            subscription_id=managed_id,
            ue_id=ue.id,
            area=area,
            types=_GEOFENCING_EVENT_TYPES,
            nef_subscription_url=str(subscription.self),
            last_state=None,
        )
        await self._redis.set(
            self.subscription_key(ue.id, managed_id), managed.model_dump_json()
        )
        LOG.info(
            "NEF geofencing subscription created for UE id=%s, subscriptionId=%s",
            ue.id,
            managed_id,
        )
        return [managed_id]

    async def delete_geofencing_subscription(
        self, ue: UE, subscription_id: str
    ) -> bool:
        key = self.subscription_key(ue.id, subscription_id)
        raw = await self._redis.get(key)
        if raw is None:
            LOG.warning(
                "NEF geofencing subscription id=%s not found in Redis for deletion",
                subscription_id,
            )
            return False
        managed = ManagedGeofencingSubscription.model_validate_json(raw)
        LOG.info(
            "Deleting NEF geofencing subscription id=%s (NEF url=%s)",
            subscription_id,
            managed.nef_subscription_url,
        )
        res = await self._client.delete(managed.nef_subscription_url)
        if res.status_code == 404:
            LOG.warning(
                "NEF monitoring subscription for geofencing id=%s not found",
                subscription_id,
            )
            await self._redis.delete(key)
            return False
        elif not res.is_success:
            raise RuntimeError(
                f"NEF geofencing subscription delete failed ({res.status_code}): {res.text}"
            )
        await self._redis.delete(key)
        return True
