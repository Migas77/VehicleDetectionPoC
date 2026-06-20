from typing import Annotated

from fastapi import Depends

from app.interfaces.location import LocationInterface
from app.settings import settings

location_interface: LocationInterface

match settings.net_apis.api:
    case "nef":
        from .nef import nef_location_interface

        location_interface = nef_location_interface
    case "camara":
        from .camara import camara_location_interface

        location_interface = camara_location_interface


async def get_location_interface() -> LocationInterface:
    return location_interface


LocationInterfaceDep = Annotated[LocationInterface, Depends(get_location_interface)]
