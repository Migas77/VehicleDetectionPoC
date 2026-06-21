import logging

from fastapi import APIRouter

from app.schemas.camara.connectivity_insights_subscriptions import (
    CloudEvent,
    NetworkQualityInsight,
)

LOG = logging.getLogger(__name__)

router = APIRouter()


@router.post("/camara/{ue_id}")
async def camara_analytics_callback(ue_id: int, body: CloudEvent) -> None:
    """Receive CloudEvent notifications from the CAMARA Connectivity Insights service."""
    LOG.info(
        "Received CAMARA CIS callback for UE id=%s: type=%s",
        ue_id,
        body.type,
    )
    data = body.data
    if isinstance(data, NetworkQualityInsight):
        LOG.info(
            "UE id=%s: NetworkQualityInsight — UL=%s, DL=%s",
            ue_id,
            data.targetMinUpstreamRate,
            data.targetMinDownstreamRate,
        )
    # TODO: propagate network quality insight to application state store
