from app.settings import settings

from .backend import CamaraQoSProfilesBackend

if settings.net_apis.api != "camara":
    raise RuntimeError(
        "QoS Profile CAMARA driver instantiated but net_apis.api isn't 'camara'"
    )

camara_qos_profiles_interface = CamaraQoSProfilesBackend()
