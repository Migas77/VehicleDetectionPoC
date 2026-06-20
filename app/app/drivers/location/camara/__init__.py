from app.drivers.location.camara.backend import CamaraLocationBackend
from app.settings import settings

if settings.net_apis.api != "camara":
    raise RuntimeError(
        "CamaraLocationBackend instantiated but net_apis.api isn't 'camara'"
    )


camara_location_interface = CamaraLocationBackend()
