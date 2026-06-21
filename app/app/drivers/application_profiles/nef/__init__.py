from app.drivers.application_profiles.nef.backend import NefApplicationProfilesBackend
from app.settings import settings

if settings.net_apis.api != "nef":
    raise RuntimeError(
        "Application Profiles NEF driver instantiated but net_apis.api isn't 'nef'"
    )

nef_application_profiles_interface = NefApplicationProfilesBackend()
