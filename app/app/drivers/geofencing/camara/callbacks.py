import logging

from fastapi import APIRouter

from app.drivers.geofencing.deps import GeofencingInterfaceDep
from app.schemas.camara.geofencing import AreaEntered, AreaLeft, CloudEvent

LOG = logging.getLogger(__name__)

router = APIRouter()


@router.post("/camara/{ue_id}/{camera_id}")
async def camara_geofencing_callback(
    ue_id: int,
    camera_id: int,
    body: CloudEvent,
    geofencing_interface: GeofencingInterfaceDep,
) -> None:
    """Receive geofencing CloudEvent notifications from the CAMARA Geofencing service."""
    LOG.info(
        "Received CAMARA geofencing callback for UE id=%s, camera id=%s: type=%s",
        ue_id,
        camera_id,
        body.type,
    )
    data = body.data
    if isinstance(data, AreaEntered):
        await geofencing_interface.register_in_camera_area(camera_id, ue_id)
        LOG.info("UE id=%s entered camera id=%s area", ue_id, camera_id)
    elif isinstance(data, AreaLeft):
        await geofencing_interface.unregister_from_camera_area(camera_id, ue_id)
        LOG.info("UE id=%s left camera id=%s area", ue_id, camera_id)
