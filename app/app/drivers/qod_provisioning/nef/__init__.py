from app.settings import settings

from .backend import NefQoDProvisioningBackend
from .callbacks import router as router

if settings.net_apis.api != "nef":
    raise RuntimeError(
        "QoD Provisioning NEF driver instantiated but net_apis.api isn't 'nef'"
    )

nef_qod_provisioning_interface = NefQoDProvisioningBackend()
