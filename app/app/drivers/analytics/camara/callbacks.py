import logging

from fastapi import APIRouter

from app.drivers.qod_provisioning import QoDProvisioningInterfaceDep
from app.drivers.ues import UEsInterfaceDep
from app.schemas.camara.connectivity_insights_subscriptions import (
    CloudEvent,
    NetworkQualityInsight,
    NetworkQualityThresholdsConfidence,
)

LOG = logging.getLogger(__name__)

router = APIRouter()

_REQUIREMENTS_UNMET = (
    NetworkQualityThresholdsConfidence.unable_to_meet_the_application_requirements
)


@router.post("/camara/{ue_supi}")
async def camara_analytics_callback(
    ue_supi: str,
    body: CloudEvent,
    qod_provisioning_interface: QoDProvisioningInterfaceDep,
    ues_interface: UEsInterfaceDep,
) -> None:
    """Receive CloudEvent notifications from the CAMARA Connectivity Insights service."""
    # LOG.info(
    #     "Received CAMARA CIS callback for UE supi=%s: type=%s",
    #     ue_supi,
    #     body.type,
    # )
    data = body.data
    if isinstance(data, NetworkQualityInsight):
        # LOG.info(
        #     "UE supi=%s: NetworkQualityInsight — UL=%s, DL=%s",
        #     ue_supi,
        #     data.targetMinUpstreamRate,
        #     data.targetMinDownstreamRate,
        # )
        if _any_requirement_unmet(
            data
        ) and await qod_provisioning_interface.can_switch_to_fallback_qos_profile(
            ue_supi
        ):
            LOG.warning(
                "UE supi=%s: analytics breach detected (UL=%s, DL=%s)",
                ue_supi,
                data.targetMinUpstreamRate,
                data.targetMinDownstreamRate,
            )
            ue = await ues_interface.get_ue_by_supi(ue_supi)
            await qod_provisioning_interface.switch_to_fallback_qos_profile(ue)
    # TODO: propagate network quality insight to application state store


def _any_requirement_unmet(insight: NetworkQualityInsight) -> bool:
    """Return True if at least one reported requirement is unmet (i.e. a breach)."""
    checks = [insight.targetMinUpstreamRate, insight.targetMinDownstreamRate]
    return any(v == _REQUIREMENTS_UNMET for v in checks)
