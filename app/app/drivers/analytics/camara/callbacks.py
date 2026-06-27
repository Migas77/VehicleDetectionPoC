import logging

from fastapi import APIRouter

from app.schemas.camara.connectivity_insights_subscriptions import (
    CloudEvent,
    NetworkQualityInsight,
)

LOG = logging.getLogger(__name__)

router = APIRouter()


@router.post("/camara/{ue_supi}")
async def camara_analytics_callback(ue_supi: str, body: CloudEvent) -> None:
    """Receive CloudEvent notifications from the CAMARA Connectivity Insights service."""
    LOG.info(
        "Received CAMARA CIS callback for UE supi=%s: type=%s",
        ue_supi,
        body.type,
    )
    data = body.data
    if isinstance(data, NetworkQualityInsight):
        LOG.info(
            "UE supi=%s: NetworkQualityInsight — UL=%s, DL=%s",
            ue_supi,
            data.targetMinUpstreamRate,
            data.targetMinDownstreamRate,
        )
    # TODO: propagate network quality insight to application state store
