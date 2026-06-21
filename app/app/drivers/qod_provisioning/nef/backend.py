import logging
from functools import cached_property
from ipaddress import IPv4Address
from typing import Any

import httpx
from pydantic import TypeAdapter

from app.interfaces.qod_provisioning import QoDProvisioningInterface
from app.schemas.nef.afSessionWithQos import AsSessionWithQoSSubscription
from app.schemas.poc import UE
from app.schemas.poc.ue_with_qos import UeWithQoS
from app.settings import settings

LOG = logging.getLogger(__name__)

_dict_adapter: TypeAdapter[dict[str, Any]] = TypeAdapter(dict[str, Any])
_list_adapter: TypeAdapter[list[AsSessionWithQoSSubscription]] = TypeAdapter(
    list[AsSessionWithQoSSubscription]
)


class NefQoDProvisioningBackend(QoDProvisioningInterface):
    """Creates and manages an indefinite AsSessionWithQoS subscription in the NEF for a camera UE."""

    @cached_property
    def _client(self) -> httpx.AsyncClient:
        return settings.create_nef_auth_client()

    async def assign_qos_profile(self, ue: UeWithQoS) -> str:
        notification_dest = (
            f"{str(settings.nef.poc_notification_url).rstrip('/')}"
            f"/callbacks/qod-provisioning/nef/{ue.id}"
        )

        if ue.ip_address_v4 is not None:
            payload = AsSessionWithQoSSubscription(
                notificationDestination=notification_dest,
                ueIpv4Addr=IPv4Address(ue.ip_address_v4),
                qosReference=ue.qos_profile.qos_profile_name,
                supportedFeatures="0",
            )
        elif ue.msisdn is not None:
            payload = AsSessionWithQoSSubscription(
                notificationDestination=notification_dest,
                gpsi=f"msisdn-{ue.msisdn}",
                qosReference=ue.qos_profile.qos_profile_name,
                supportedFeatures="0",
            )
        else:
            raise ValueError(
                f"Cannot identify UE id={ue.id} for NEF: "
                "neither ip_address_v4 nor msisdn is set"
            )

        url = f"/nef/api/v1/3gpp-as-session-with-qos/v1/{settings.poc_af_id}/subscriptions"
        LOG.info(
            "Creating NEF AsSessionWithQoS subscription for UE id=%s, qosRef=%s",
            ue.id,
            ue.qos_profile.qos_profile_name,
        )
        res = await self._client.post(
            url,
            content=payload.model_dump_json(exclude_unset=True),
            headers={"Content-Type": "application/json"},
        )
        if not res.is_success:
            raise RuntimeError(
                f"NEF AsSessionWithQoS subscription failed ({res.status_code}): {res.text}"
            )
        subscription = AsSessionWithQoSSubscription.model_validate_json(res.content)
        if subscription.self is None:
            raise RuntimeError(
                f"NEF subscription response missing 'self' link for UE id={ue.id}"
            )
        sub_id = self._extract_subscription_id(str(subscription.self))
        LOG.info(
            "NEF subscription created for UE id=%s, subscriptionId=%s",
            ue.id,
            sub_id,
        )
        return sub_id

    async def get_qod_provisioning(self, provisioning_id: str) -> dict[str, Any]:
        url = f"/nef/api/v1/3gpp-as-session-with-qos/v1/{settings.poc_af_id}/subscriptions/{provisioning_id}"
        res = await self._client.get(url)
        if not res.is_success:
            raise RuntimeError(
                f"NEF AsSessionWithQoS get failed ({res.status_code}): {res.text}"
            )
        return _dict_adapter.validate_json(res.content)

    async def delete_qod_provisioning(self, provisioning_id: str) -> bool:
        LOG.info("Deleting NEF AsSessionWithQoS subscription id=%s", provisioning_id)
        url = f"/nef/api/v1/3gpp-as-session-with-qos/v1/{settings.poc_af_id}/subscriptions/{provisioning_id}"
        res = await self._client.delete(url)
        if res.status_code == 404:
            LOG.warning(
                "NEF AsSessionWithQoS subscription id=%s not found for deletion",
                provisioning_id,
            )
            return False
        if not res.is_success:
            raise RuntimeError(
                f"NEF AsSessionWithQoS delete failed ({res.status_code}): {res.text}"
            )
        LOG.info("NEF subscription deleted, subscriptionId=%s", provisioning_id)
        return True

    async def retrieve_qod_provisioning_by_device(self, ue: UE) -> str | None:
        url = f"/nef/api/v1/3gpp-as-session-with-qos/v1/{settings.poc_af_id}/subscriptions"
        res = await self._client.get(url)
        if not res.is_success:
            raise RuntimeError(
                f"NEF AsSessionWithQoS list failed ({res.status_code}): {res.text}"
            )
        subscriptions = _list_adapter.validate_json(res.content)
        match = self._find_subscription_by_device(subscriptions, ue)
        if match is None or match.self is None:
            return None
        return self._extract_subscription_id(str(match.self))

    @staticmethod
    def _find_subscription_by_device(
        subscriptions: list[AsSessionWithQoSSubscription], ue: UE
    ) -> AsSessionWithQoSSubscription | None:
        """Return the subscription matching the UE's IPv4 address or MSISDN, or None."""
        for sub in subscriptions:
            if ue.ip_address_v4 is not None and sub.ueIpv4Addr == IPv4Address(
                ue.ip_address_v4
            ):
                return sub
            if ue.msisdn is not None and sub.gpsi == f"msisdn-{ue.msisdn}":
                return sub
        return None

    @staticmethod
    def _extract_subscription_id(self_link: str) -> str:
        """Extract the subscription ID from the last path segment of the NEF 'self' URL."""
        return self_link.rstrip("/").split("/")[-1]
