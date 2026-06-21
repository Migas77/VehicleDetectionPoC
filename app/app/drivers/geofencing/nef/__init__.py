from app.drivers.geofencing.nef.backend import NefGeofencingBackend
from app.drivers.geofencing.nef.callbacks import router as router
from app.settings import settings

if settings.net_apis.api != "nef":
    raise RuntimeError(
        "Geofencing NEF driver instantiated but net_apis.api isn't 'nef'"
    )

nef_geofencing_interface = NefGeofencingBackend()
