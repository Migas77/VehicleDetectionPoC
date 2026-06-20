from typing import Annotated

from fastapi import Depends

from app.interfaces.qos_profiles import QoSProfilesInterface
from app.settings import settings

qos_profiles_interface: QoSProfilesInterface

match settings.net_apis.api:
    case "nef":
        from .nef import nef_qos_profiles_interface

        qos_profiles_interface = nef_qos_profiles_interface
    case "camara":
        from .camara import camara_qos_profiles_interface

        qos_profiles_interface = camara_qos_profiles_interface


async def get_qos_profiles_interface() -> QoSProfilesInterface:
    return qos_profiles_interface


QoSProfilesInterfaceDep = Annotated[
    QoSProfilesInterface, Depends(get_qos_profiles_interface)
]
