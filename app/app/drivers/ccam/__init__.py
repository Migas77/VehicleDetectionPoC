from typing import Annotated

from fastapi import Depends

from app.interfaces.ccam import CcamInterface
from app.settings import settings

ccam_interface: CcamInterface

match settings.ccam_broker.backend:
    case "mqtt":
        from .mqtt import mqtt_ccam_interface

        ccam_interface = mqtt_ccam_interface
    case "mock":
        from .mock import mock_ccam_interface

        ccam_interface = mock_ccam_interface


async def get_ccam_interface() -> CcamInterface:
    return ccam_interface


CcamInterfaceDep = Annotated[CcamInterface, Depends(get_ccam_interface)]
