from fastapi import APIRouter

from app.interfaces.geofencing import GeofencingInterface
from app.settings import settings

geofencing_interface: GeofencingInterface
router = APIRouter(prefix="/callbacks/geofencing")

match settings.net_apis.api:
    case "nef":
        from .nef import nef_geofencing_interface
        from .nef import router as nef_router

        geofencing_interface = nef_geofencing_interface
        router.include_router(nef_router)
    case "camara":
        from .camara import camara_geofencing_interface
        from .camara import router as camara_router

        geofencing_interface = camara_geofencing_interface
        router.include_router(camara_router)
