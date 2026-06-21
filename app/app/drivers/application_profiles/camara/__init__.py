from app.drivers.application_profiles.camara.backend import (
    CamaraApplicationProfilesBackend,
)
from app.settings import settings

if settings.net_apis.api != "camara":
    raise RuntimeError(
        "Application Profiles CAMARA driver instantiated but net_apis.api isn't 'camara'"
    )

camara_application_profiles_interface = CamaraApplicationProfilesBackend()
