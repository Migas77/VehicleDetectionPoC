from typing import Annotated

from fastapi import Depends

from app.drivers.ccam.backend import MqttCcamBackend
from app.interfaces.ccam import CcamInterface

ccam_interface: CcamInterface = MqttCcamBackend()


async def get_ccam_interface() -> CcamInterface:
    return ccam_interface


CcamInterfaceDep = Annotated[CcamInterface, Depends(get_ccam_interface)]
