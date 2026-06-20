from app.settings import settings

from .backend import CamaraQoDProvisioningBackend
from .callbacks import router as router

if settings.net_apis.api != "camara":
    raise RuntimeError(
        "QoD Provisioning CAMARA driver instantiated but net_apis.api isn't 'camara'"
    )

camara_qod_provisioning_interface = CamaraQoDProvisioningBackend()
