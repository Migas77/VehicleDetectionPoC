import logging

from fastapi import APIRouter

from app.drivers.geofencing.deps import GeofencingInterfaceDep
from app.schemas.camara.geofencing import AreaEntered, AreaLeft, CloudEvent

LOG = logging.getLogger(__name__)

router = APIRouter()


@router.post("/camara/{ue_supi}/{camera_supi}")
async def camara_geofencing_callback(
    ue_supi: str,
    camera_supi: str,
    body: CloudEvent,
    geofencing_interface: GeofencingInterfaceDep,
) -> None:
    """Receive geofencing CloudEvent notifications from the CAMARA Geofencing service."""
    LOG.info(
        "Received CAMARA geofencing callback for UE supi=%s, camera supi=%s: type=%s",
        ue_supi,
        camera_supi,
        body.type,
    )
    data = body.data
    if isinstance(data, AreaEntered):
        await geofencing_interface.register_in_camera_area(camera_supi, ue_supi)
        LOG.info("UE supi=%s entered camera supi=%s area", ue_supi, camera_supi)
    elif isinstance(data, AreaLeft):
        await geofencing_interface.unregister_from_camera_area(camera_supi, ue_supi)
        LOG.info("UE supi=%s left camera supi=%s area", ue_supi, camera_supi)
