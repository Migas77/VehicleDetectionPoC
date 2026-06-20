from typing import Annotated

from fastapi import APIRouter, Depends

from app.interfaces.qod_provisioning import QoDProvisioningInterface
from app.settings import settings

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


async def get_qod_provisioning_interface() -> QoDProvisioningInterface:
    return qod_provisioning_interface


QoDProvisioningInterfaceDep = Annotated[
    QoDProvisioningInterface, Depends(get_qod_provisioning_interface)
]
