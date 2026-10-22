import logging
import time
from functools import cached_property

import httpx

from app.drivers.capif_auth import discover_camara_url
from app.interfaces.analytics import AnalyticsInterface
from app.schemas.camara.application_profiles import ApplicationProfileId
from app.schemas.camara.connectivity_insights_subscriptions import (
    CreateSubscriptionDetail,
    SubscriptionEventType,
    SubscriptionRequest,
    SubscriptionRequestTypeAdapter,
    CISSubscriptionTypeAdapter,
)
from app.schemas.camara.common import ApplicationServer
from app.schemas.camara.device import Device
from app.schemas.camara.subscriptions import (
    HTTPSubscriptionRequest,
    Protocol,
    SubscriptionConfig,
)
from app.schemas.poc.ue_with_qos import UeWithQoS
from app.settings import settings

LOG = logging.getLogger(__name__)

# Concrete CIS HTTP subscription request, with the generic event type / detail bound
NetworkQualitySubscriptionRequest = HTTPSubscriptionRequest[
    SubscriptionEventType, CreateSubscriptionDetail
]


class CamaraAnalyticsBackend(AnalyticsInterface):
    """Creates and deletes Connectivity Insights Subscriptions via the CAMARA CIS API."""

    def __init__(self) -> None:
        super().__init__()
        self._notification_url = settings.camara_notification_url

    @cached_property
    def _client(self) -> httpx.AsyncClient:
        return settings.create_camara_client()

    @staticmethod
    def _build_device(ue: UeWithQoS) -> Device:
        # CIS API requires phoneNumber or networkAccessIdentifier — not ipv4Address; include both when available
        phone = (
            (ue.msisdn if ue.msisdn.startswith("+") else f"+{ue.msisdn}")
            if ue.msisdn
            else None
        )
        network_access_id = ue.external_identifier
        if phone is None and network_access_id is None:
            raise ValueError(
                f"Cannot identify device for UE supi={ue.supi} for CIS subscription: "
                "msisdn or external_identifier is required"
            )
        return Device(phoneNumber=phone, networkAccessIdentifier=network_access_id)

    async def create_analytics_subscription(
        self, ue: UeWithQoS, application_profile_id: ApplicationProfileId
    ) -> str:
        sink = f"{self._notification_url}/callbacks/analytics/camara/{ue.supi}"
        payload: SubscriptionRequest = NetworkQualitySubscriptionRequest(
            sink=sink,
            types=[
                SubscriptionEventType.org_camaraproject_connectivity_insights_subscriptions_v0_network_quality
            ],
            protocol=Protocol.HTTP,
            config=SubscriptionConfig(
                subscriptionDetail=CreateSubscriptionDetail(
                    device=self._build_device(ue),
                    applicationServer=ApplicationServer(
                        ipv4Address=settings.poc_app_server
                    ),
                    applicationProfileId=application_profile_id,
                )
            ),
        )
        # LOG.info(
        #     "Creating CAMARA CIS subscription for UE supi=%s, applicationProfileId=%s",
        #     ue.supi,
        #     application_profile_id,
        # )
        url = discover_camara_url(
            fallback="/connectivity-insights-subscriptions/v0.6/subscriptions",
            resource_name="Create Subscription",
            api_name_filter="connectivity-insights-subscriptions",
            operation="POST",
        )
        body = SubscriptionRequestTypeAdapter.dump_json(payload, exclude_unset=True)
        # await asyncio.sleep(8)  # benchmark: measure from a cold http connection
        LOG.info("DELAY: request sent")
        _bench_start_ns = time.perf_counter_ns()
        res = await self._client.post(
            url,
            content=body,
            headers={"Content-Type": "application/json"},
        )
        LOG.info("DELAY: request responded")
        _bench_elapsed_ns = time.perf_counter_ns() - _bench_start_ns
        LOG.info(
            'BENCHMARK: {"api": "CAMARA", "resource": "Create Subscription", '
            '"filter": "connectivity-insights-subscriptions", "op": "POST", '
            '"x_correlator": "%s", "ue": "%s", "time_ns": %d, "status": %d}',
            res.request.headers.get("x-correlator") or "",
            ue.supi,
            _bench_elapsed_ns,
            res.status_code,
        )
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA CIS subscription failed ({res.status_code}): {res.text}"
            )
        subscription = CISSubscriptionTypeAdapter.validate_json(res.content)
        sub_id = subscription.id
        await self._redis.set(self._subscription_key(ue.supi, sub_id), sub_id)
        # LOG.info(
        #     "CAMARA CIS subscription created for UE supi=%s, subscriptionId=%s",
        #     ue.supi,
        #     sub_id,
        # )
        return sub_id

    async def delete_analytics_subscription(
        self, ue: UeWithQoS, subscription_id: str
    ) -> bool:
        # LOG.info("Deleting CAMARA CIS subscription id=%s", subscription_id)
        res = await self._client.delete(
            discover_camara_url(
                fallback="/connectivity-insights-subscriptions/v0.6/subscriptions/{subscriptionId}",
                resource_name="Delete Subscription By Id",
                api_name_filter="connectivity-insights-subscriptions",
                operation="DELETE",
            ).format(subscriptionId=subscription_id)
        )
        if res.status_code == 404:
            LOG.warning(
                "CAMARA CIS subscription id=%s not found for deletion", subscription_id
            )
            await self._redis.delete(self._subscription_key(ue.supi, subscription_id))
            return False
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA CIS subscription delete failed ({res.status_code}): {res.text}"
            )
        await self._redis.delete(self._subscription_key(ue.supi, subscription_id))
        # LOG.info("CAMARA CIS subscription id=%s deleted", subscription_id)
        return True
