from app.settings import settings

from .backend import NefQoSProfilesBackend

if settings.net_apis.api != "nef":
    raise RuntimeError(
        "QoS Profile NEF driver instantiated but net_apis.api isn't 'nef'"
    )

nef_qos_profiles_interface = NefQoSProfilesBackend()
