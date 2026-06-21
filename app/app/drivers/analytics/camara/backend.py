import logging

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
        self._client = settings.create_camara_client()
        self._notification_url = settings.camara_notification_url

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
                f"Cannot identify device for UE id={ue.id} for CIS subscription: "
                "msisdn or external_identifier is required"
            )
        return Device(phoneNumber=phone, networkAccessIdentifier=network_access_id)

    async def create_analytics_subscription(
        self, ue: UeWithQoS, application_profile_id: ApplicationProfileId
    ) -> str:
        sink = f"{self._notification_url}/callbacks/analytics/camara/{ue.id}"
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
        LOG.info(
            "Creating CAMARA CIS subscription for UE id=%s, applicationProfileId=%s",
            ue.id,
            application_profile_id,
        )
        res = await self._client.post(
            "/connectivity-insights-subscriptions/v0.6/subscriptions",
            content=SubscriptionRequestTypeAdapter.dump_json(
                payload, exclude_unset=True
            ),
            headers={"Content-Type": "application/json"},
        )
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA CIS subscription failed ({res.status_code}): {res.text}"
            )
        subscription = CISSubscriptionTypeAdapter.validate_json(res.content)
        sub_id = subscription.id
        LOG.info(
            "CAMARA CIS subscription created for UE id=%s, subscriptionId=%s",
            ue.id,
            sub_id,
        )
        return sub_id

    async def delete_analytics_subscription(self, subscription_id: str) -> bool:
        LOG.info("Deleting CAMARA CIS subscription id=%s", subscription_id)
        res = await self._client.delete(
            f"/connectivity-insights-subscriptions/v0.6/subscriptions/{subscription_id}"
        )
        if res.status_code == 404:
            LOG.warning(
                "CAMARA CIS subscription id=%s not found for deletion", subscription_id
            )
            return False
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA CIS subscription delete failed ({res.status_code}): {res.text}"
            )
        LOG.info("CAMARA CIS subscription id=%s deleted", subscription_id)
        return True
