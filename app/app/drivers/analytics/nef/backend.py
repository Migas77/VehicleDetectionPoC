import logging
from functools import cached_property

import httpx

from app.interfaces.analytics import AnalyticsInterface
from app.schemas.camara.application_profiles import ApplicationProfileId
from app.schemas.nef.analytics_exposure import (
    AnalyticsEvent,
    AnalyticsEventFilterSubsc,
    AnalyticsEventSubsc,
    AnalyticsExposureSubsc,
    AnalyticsSubset,
    EventReportingRequirement,
    NotificationMethod,
    ReportingInformation,
    TargetUeId, AddrFqdn, IpAddr, IpAddr1,
)
from app.schemas.poc.ue_with_qos import UeWithQoS
from app.settings import settings

LOG = logging.getLogger(__name__)


class NefAnalyticsBackend(AnalyticsInterface):
    """Subscribes to WLAN_PERFORMANCE analytics events via the NEF Analytics Exposure API."""

    @cached_property
    def _client(self) -> httpx.AsyncClient:
        return settings.create_nef_auth_client()

    async def create_analytics_subscription(
        self, ue: UeWithQoS, application_profile_id: ApplicationProfileId
    ) -> str:
        if ue.msisdn is None:
            raise ValueError(
                f"Cannot create analytics subscription for UE id={ue.id}: msisdn is required"
            )
        notification_url = (
            f"{str(settings.nef.poc_notification_url).rstrip('/')}"
            f"/callbacks/analytics/nef/{ue.id}"
        )
        payload = AnalyticsExposureSubsc(
            analyEventsSubs=[
                AnalyticsEventSubsc(
                    analyEvent=AnalyticsEvent.WLAN_PERFORMANCE,
                    analyEventFilter=AnalyticsEventFilterSubsc(
                        appServerAddrs=[
                            # Needed for current implementations of WLAN_PERFORMANCE event
                            # to specify target server address
                            AddrFqdn(ipAddr=IpAddr(root=IpAddr1(ipv4Addr=settings.poc_app_server)))
                        ],
                        listOfAnaSubsets=[
                            AnalyticsSubset.TRAFFIC_INFO,
                            AnalyticsSubset.NUMBER_OF_UES,
                        ],
                        extraReportReq=EventReportingRequirement(
                            offsetPeriod=settings.analytics.offset_period
                        ),
                        temporalGranSize=settings.analytics.temporal_gran_size,
                    ),
                    tgtUe=TargetUeId(gpsi=f"msisdn-{ue.msisdn}"),
                )
            ],
            analyRepInfo=ReportingInformation(
                notifMethod=NotificationMethod.PERIODIC,
                repPeriod=settings.analytics.rep_period,
            ),
            notifUri=notification_url,
            notifId=str(
                application_profile_id
            ),  # round-trips in callback for correlation
        )
        url = (
            f"/nef/api/v1/3gpp-analyticsexposure/v1/{settings.poc_af_id}/subscriptions"
        )
        LOG.info(
            "Creating NEF analytics subscription for UE id=%s, applicationProfileId=%s",
            ue.id,
            application_profile_id,
        )
        res = await self._client.post(
            url,
            content=payload.model_dump_json(exclude_none=True),
            headers={"Content-Type": "application/json"},
        )
        if not res.is_success:
            raise RuntimeError(
                f"NEF analytics subscription failed ({res.status_code}): {res.text}"
            )
        subscription = AnalyticsExposureSubsc.model_validate_json(res.content)
        if subscription.self is None:
            raise RuntimeError(
                f"NEF analytics subscription response missing 'self' link for UE id={ue.id}"
            )
        sub_id = self._extract_subscription_id(str(subscription.self))
        await self._redis.set(self._subscription_key(ue.id, sub_id), sub_id)
        LOG.info(
            "NEF analytics subscription created for UE id=%s, subscriptionId=%s",
            ue.id,
            sub_id,
        )
        return sub_id

    async def delete_analytics_subscription(
        self, ue: UeWithQoS, subscription_id: str
    ) -> bool:
        LOG.info("Deleting NEF analytics subscription id=%s", subscription_id)
        url = (
            f"/nef/api/v1/3gpp-analyticsexposure/v1/"
            f"{settings.poc_af_id}/subscriptions/{subscription_id}"
        )
        res = await self._client.delete(url)
        if res.status_code == 404:
            LOG.warning(
                "NEF analytics subscription id=%s not found for deletion",
                subscription_id,
            )
            await self._redis.delete(self._subscription_key(ue.id, subscription_id))
            return False
        if not res.is_success:
            raise RuntimeError(
                f"NEF analytics subscription delete failed ({res.status_code}): {res.text}"
            )
        await self._redis.delete(self._subscription_key(ue.id, subscription_id))
        LOG.info(
            "NEF analytics subscription deleted, subscriptionId=%s", subscription_id
        )
        return True

    @staticmethod
    def _extract_subscription_id(self_link: str) -> str:
        """Extract the subscription ID from the last path segment of the NEF 'self' URL."""
        return self_link.rstrip("/").split("/")[-1]
