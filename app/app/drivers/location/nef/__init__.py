from app.drivers.location.nef.backend import NefLocationBackend
from app.settings import settings

if settings.net_apis.api != "nef":
    raise RuntimeError("NefLocationBackend instantiated but net_apis.api isn't 'nef'")


nef_location_interface = NefLocationBackend()
