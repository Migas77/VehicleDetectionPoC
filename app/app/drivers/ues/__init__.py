from typing import Annotated

from fastapi import Depends

from app.drivers.ues.nef import nef_ues_interface
from app.interfaces.ues import UEsInterface

ues_interface: UEsInterface = nef_ues_interface


async def get_ues_interface() -> UEsInterface:
    return ues_interface


UEsInterfaceDep = Annotated[UEsInterface, Depends(get_ues_interface)]
