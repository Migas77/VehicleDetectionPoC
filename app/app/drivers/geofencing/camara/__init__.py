from app.drivers.geofencing.camara.backend import CamaraGeofencingBackend
from app.drivers.geofencing.camara.callbacks import router as router
from app.settings import settings

if settings.net_apis.api != "camara":
    raise RuntimeError(
        "Geofencing CAMARA driver instantiated but net_apis.api isn't 'camara'"
    )

camara_geofencing_interface = CamaraGeofencingBackend()
