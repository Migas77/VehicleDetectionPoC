import logging

from fastapi import APIRouter

from app.schemas.nef.afSessionWithQos import UserPlaneNotificationData

LOG = logging.getLogger(__name__)

router = APIRouter()


@router.post("/nef/{ue_supi}")
async def nef_qos_callback(ue_supi: str, body: UserPlaneNotificationData) -> None:
    """Receive UserPlaneNotificationData events from the NEF for a given UE."""
    LOG.info(
        "Received NEF QoS callback for UE supi=%s: %s event(s)",
        ue_supi,
        len(body.eventReports),
    )
    for report in body.eventReports:
        LOG.info("  UE supi=%s event: %s", ue_supi, report.event)
    # TODO: update UE QoS state in application state store
