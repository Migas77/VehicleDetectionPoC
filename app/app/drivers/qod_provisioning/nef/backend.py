import logging
import time
from functools import cached_property
from ipaddress import IPv4Address
from typing import Any

import httpx
from pydantic import TypeAdapter

from app.drivers.capif_auth import discover_nef_url
from app.interfaces.qod_provisioning import QoDProvisioningInterface
from app.schemas.nef.afSessionWithQos import (
    AsSessionWithQoSSubscription,
    AsSessionWithQoSSubscriptionPatch,
)
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
        return settings.create_nef_exposure_client()

    async def _create_provisioning(self, ue: UeWithQoS) -> str:
        notification_dest = (
            f"{str(settings.nef.poc_notification_url).rstrip('/')}"
            f"/callbacks/qod-provisioning/nef/{ue.supi}"
        )

        if ue.ip_address_v4 is not None:
            payload = AsSessionWithQoSSubscription(
                notificationDestination=notification_dest,
                ueIpv4Addr=IPv4Address(ue.ip_address_v4),
                dnn=settings.nef.qos_dnn,
                qosReference=ue.qos_profile.qos_profile_name,
                supportedFeatures="0",
            )
        elif ue.msisdn is not None:
            payload = AsSessionWithQoSSubscription(
                notificationDestination=notification_dest,
                gpsi=f"msisdn-{ue.msisdn}",
                dnn=settings.nef.qos_dnn,
                qosReference=ue.qos_profile.qos_profile_name,
                supportedFeatures="0",
            )
        else:
            raise ValueError(
                f"Cannot identify UE supi={ue.supi} for NEF: "
                "neither ip_address_v4 nor msisdn is set"
            )

        url = discover_nef_url(
            fallback="/nef/api/v1/3gpp-as-session-with-qos/v1/{scsAsId}/subscriptions",
            resource_name="Create Subscription",
            api_name_filter="as-session-with-qos",
            operation="POST",
        ).format(scsAsId=settings.poc_af_id)
        # LOG.info(
        #     "Creating NEF AsSessionWithQoS subscription for UE supi=%s, qosRef=%s",
        #     ue.supi,
        #     ue.qos_profile.qos_profile_name,
        # )
        body = payload.model_dump_json(exclude_unset=True)
        # await asyncio.sleep(8)  # benchmark: measure from a cold http connection
        _bench_start_ns = time.perf_counter_ns()
        res = await self._client.post(
            url,
            content=body,
            headers={"Content-Type": "application/json"},
        )
        _bench_elapsed_ns = time.perf_counter_ns() - _bench_start_ns
        LOG.info(
            'BENCHMARK: {"api": "NEF", "resource": "Create Subscription", '
            '"filter": "as-session-with-qos", "op": "POST", '
            '"x_correlator": "%s", "ue": "%s", "time_ns": %d, "status": %d}',
            res.request.headers.get("x-correlator") or "",
            ue.supi,
            _bench_elapsed_ns,
            res.status_code,
        )
        if not res.is_success:
            raise RuntimeError(
                f"NEF AsSessionWithQoS subscription failed ({res.status_code}): {res.text}"
            )
        subscription = AsSessionWithQoSSubscription.model_validate_json(res.content)
        if subscription.self is None:
            raise RuntimeError(
                f"NEF subscription response missing 'self' link for UE supi={ue.supi}"
            )
        sub_id = self._extract_subscription_id(str(subscription.self))
        # LOG.info(
        #     "NEF subscription created for UE supi=%s, subscriptionId=%s",
        #     ue.supi,
        #     sub_id,
        # )
        return sub_id

    async def _replace_provisioning(self, provisioning_id: str, ue: UeWithQoS) -> str:
        """PATCH the subscription's qosReference in place.

        Unlike DELETE + POST, the NEF doesn't revert the UE's QoS first, so if the
        new profile is rejected the previously applied one remains in place.
        """
        qos_reference = ue.qos_profile.qos_profile_name
        subscription = AsSessionWithQoSSubscription.model_validate(
            await self.get_qod_provisioning(provisioning_id)
        )
        if subscription.qosReference == qos_reference:
            # the NEF only reallocates (and notifies) when the profile changes
            LOG.warning(
                "UE supi=%s: subscription id=%s already references %s, nothing to change",
                ue.supi,
                provisioning_id,
                qos_reference,
            )
            return provisioning_id

        url = discover_nef_url(
            fallback="/nef/api/v1/3gpp-as-session-with-qos/v1/{scsAsId}/subscriptions/{subscriptionId}",
            resource_name="Patch Subscription",
            api_name_filter="as-session-with-qos",
            operation="PATCH",
        ).format(scsAsId=settings.poc_af_id, subscriptionId=provisioning_id)
        payload = AsSessionWithQoSSubscriptionPatch(qosReference=qos_reference)

        await self._request_qos_profile(ue.supi, qos_reference, provisioning_id)
        try:
            res = await self._client.patch(
                url,
                content=payload.model_dump_json(exclude_unset=True),
                headers={"Content-Type": "application/json"},
            )
            if not res.is_success:
                raise RuntimeError(
                    f"NEF AsSessionWithQoS patch failed ({res.status_code}): {res.text}"
                )
        except Exception:
            await self._cancel_qos_request(ue.supi, qos_reference)
            raise
        return provisioning_id

    async def get_qod_provisioning(self, provisioning_id: str) -> dict[str, Any]:
        url = discover_nef_url(
            fallback="/nef/api/v1/3gpp-as-session-with-qos/v1/{scsAsId}/subscriptions/{subscriptionId}",
            resource_name="Read Subscription",
            api_name_filter="as-session-with-qos",
            operation="GET",
        ).format(scsAsId=settings.poc_af_id, subscriptionId=provisioning_id)
        res = await self._client.get(url)
        if not res.is_success:
            raise RuntimeError(
                f"NEF AsSessionWithQoS get failed ({res.status_code}): {res.text}"
            )
        return _dict_adapter.validate_json(res.content)

    async def delete_qod_provisioning(self, provisioning_id: str) -> bool:
        # LOG.info("Deleting NEF AsSessionWithQoS subscription id=%s", provisioning_id)
        url = discover_nef_url(
            fallback="/nef/api/v1/3gpp-as-session-with-qos/v1/{scsAsId}/subscriptions/{subscriptionId}",
            resource_name="Delete Subscription",
            api_name_filter="as-session-with-qos",
            operation="DELETE",
        ).format(scsAsId=settings.poc_af_id, subscriptionId=provisioning_id)
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
        # LOG.info("NEF subscription deleted, subscriptionId=%s", provisioning_id)
        return True

    async def retrieve_qod_provisioning_by_device(self, ue: UE) -> str | None:
        url = discover_nef_url(
            fallback="/nef/api/v1/3gpp-as-session-with-qos/v1/{scsAsId}/subscriptions",
            resource_name="Read Active Subscriptions",
            api_name_filter="as-session-with-qos",
            operation="GET",
        ).format(scsAsId=settings.poc_af_id)
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
