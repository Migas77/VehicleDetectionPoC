import logging
from ipaddress import IPv4Address, IPv6Address

from app.interfaces.geofencing import GeofencingInterface
from app.schemas.camara.device import Device, DeviceIpv4Addr
from app.schemas.camara.geofencing import (
    AreaType,
    Circle,
    SubscriptionDetail,
    SubscriptionEventType,
    SubscriptionTypeAdapter,
)
from app.schemas.camara.subscriptions import (
    HTTPSubscriptionRequest,
    Protocol,
    SubscriptionConfig,
)
from app.schemas.poc.area import SurveyedArea
from app.schemas.poc.ue import UE
from app.settings import settings

LOG = logging.getLogger(__name__)

# Concrete geofencing HTTP subscription request, with the generic event type / detail bound
GeofencingSubscriptionRequest = HTTPSubscriptionRequest[
    SubscriptionEventType, SubscriptionDetail
]

# One subscription per event type — the CAMARA request schema enforces a single type each
_GEOFENCING_EVENT_TYPES = [
    SubscriptionEventType.v0_area_entered,
    SubscriptionEventType.v0_area_left,
]


class CamaraGeofencingBackend(GeofencingInterface):
    """Creates and deletes Geofencing Subscriptions via the CAMARA Geofencing Subscriptions API."""

    def __init__(self) -> None:
        super().__init__()
        self._client = settings.create_camara_client()
        self._notification_url = settings.camara_notification_url

    @staticmethod
    def _build_device(ue: UE) -> Device:
        # Geofencing API identifies the device by phone number and/or IP address
        phone = (
            (ue.msisdn if ue.msisdn.startswith("+") else f"+{ue.msisdn}")
            if ue.msisdn
            else None
        )
        ipv4 = (
            DeviceIpv4Addr(
                publicAddress=IPv4Address(ue.ip_address_v4),
                privateAddress=IPv4Address(ue.ip_address_v4),
            )
            if ue.ip_address_v4
            else None
        )
        ipv6 = IPv6Address(ue.ip_address_v6) if ue.ip_address_v6 else None
        if phone is None and ipv4 is None and ipv6 is None:
            raise ValueError(
                f"Cannot identify device for UE id={ue.id} for geofencing subscription: "
                "msisdn, ip_address_v4 or ip_address_v6 is required"
            )
        return Device(phoneNumber=phone, ipv4Address=ipv4, ipv6Address=ipv6)

    async def create_geofencing_subscription(
        self, ue: UE, area: SurveyedArea
    ) -> list[str]:
        sink = f"{self._notification_url}/callbacks/geofencing/camara/{ue.id}/{area.camera_id}"
        detail = SubscriptionDetail(
            device=self._build_device(ue),
            area=Circle(
                areaType=AreaType.CIRCLE, center=area.center, radius=area.radius
            ),
        )
        subscription_ids: list[str] = []
        for event_type in _GEOFENCING_EVENT_TYPES:
            payload = GeofencingSubscriptionRequest(
                sink=sink,
                types=[event_type],
                protocol=Protocol.HTTP,
                config=SubscriptionConfig(subscriptionDetail=detail),
            )
            LOG.info(
                "Creating CAMARA geofencing subscription for UE id=%s, camera id=%s, type=%s",
                ue.id,
                area.camera_id,
                event_type.value,
            )
            res = await self._client.post(
                "/geofencing-subscriptions/v0.4/subscriptions",
                content=payload.model_dump_json(exclude_unset=True),
                headers={"Content-Type": "application/json"},
            )
            if not res.is_success:
                raise RuntimeError(
                    f"CAMARA geofencing subscription failed ({res.status_code}): {res.text}"
                )
            subscription = SubscriptionTypeAdapter.validate_json(res.content)
            sub_id = subscription.id
            await self._redis.set(self.subscription_key(ue.id, sub_id), sub_id)
            subscription_ids.append(sub_id)
            LOG.info(
                "CAMARA geofencing subscription created for UE id=%s, subscriptionId=%s",
                ue.id,
                sub_id,
            )
        return subscription_ids

    async def delete_geofencing_subscription(
        self, ue: UE, subscription_id: str
    ) -> bool:
        LOG.info("Deleting CAMARA geofencing subscription id=%s", subscription_id)
        res = await self._client.delete(
            f"/geofencing-subscriptions/v0.4/subscriptions/{subscription_id}"
        )
        if res.status_code == 404:
            LOG.warning(
                "CAMARA geofencing subscription id=%s not found for deletion",
                subscription_id,
            )
            await self._redis.delete(self.subscription_key(ue.id, subscription_id))
            return False
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA geofencing subscription delete failed ({res.status_code}): {res.text}"
            )
        await self._redis.delete(self.subscription_key(ue.id, subscription_id))
        LOG.info("CAMARA geofencing subscription id=%s deleted", subscription_id)
        return True
