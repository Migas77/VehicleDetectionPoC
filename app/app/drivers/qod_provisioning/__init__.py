from fastapi import APIRouter

from app.interfaces.qod_provisioning import QoDProvisioningInterface
from app.settings import settings

from .deps import QoDProvisioningInterfaceDep as QoDProvisioningInterfaceDep
from .deps import get_qod_provisioning_interface as get_qod_provisioning_interface

qod_provisioning_interface: QoDProvisioningInterface
router = APIRouter(prefix="/callbacks/qod-provisioning")

match settings.net_apis.api:
    case "nef":
        from .nef import nef_qod_provisioning_interface
        from .nef import router as nef_router

        qod_provisioning_interface = nef_qod_provisioning_interface
        router.include_router(nef_router)
    case "camara":
        from .camara import camara_qod_provisioning_interface
        from .camara import router as camara_router

        qod_provisioning_interface = camara_qod_provisioning_interface
        router.include_router(camara_router)
