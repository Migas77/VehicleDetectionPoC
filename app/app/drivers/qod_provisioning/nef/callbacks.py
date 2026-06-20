import logging

from fastapi import APIRouter

from app.schemas.nef.afSessionWithQos import UserPlaneNotificationData

LOG = logging.getLogger(__name__)

router = APIRouter()


@router.post("/nef/{ue_id}")
async def nef_qos_callback(ue_id: int, body: UserPlaneNotificationData) -> None:
    """Receive UserPlaneNotificationData events from the NEF for a given UE."""
    LOG.info(
        "Received NEF QoS callback for UE id=%s: %s event(s)",
        ue_id,
        len(body.eventReports),
    )
    for report in body.eventReports:
        LOG.info("  UE id=%s event: %s", ue_id, report.event)
    # TODO: update UE QoS state in application state store
