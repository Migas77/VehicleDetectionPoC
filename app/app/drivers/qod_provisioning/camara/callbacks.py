import logging

from fastapi import APIRouter

from app.schemas.camara.qodProvisioning import CloudEvent

LOG = logging.getLogger(__name__)

router = APIRouter()


@router.post("/camara/{ue_id}")
async def camara_qos_callback(ue_id: int, body: CloudEvent) -> None:
    """Receive CloudEvent status-changed notifications from the CAMARA gateway for a given UE."""
    LOG.info(
        "Received CAMARA QoD provisioning callback for UE id=%s: "
        "type=%s, provisioningId=%s, status=%s",
        ue_id,
        body.type,
        body.data.provisioningId,
        body.data.status,
    )
    # TODO: update UE QoS state in application state store
