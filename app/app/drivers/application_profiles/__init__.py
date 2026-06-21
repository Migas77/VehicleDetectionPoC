from typing import Annotated

from fastapi import Depends

from app.interfaces.application_profiles import ApplicationProfilesInterface
from app.settings import settings

application_profiles_interface: ApplicationProfilesInterface

match settings.net_apis.api:
    case "nef":
        from .nef import nef_application_profiles_interface

        application_profiles_interface = nef_application_profiles_interface
    case "camara":
        from .camara import camara_application_profiles_interface

        application_profiles_interface = camara_application_profiles_interface


async def get_application_profiles_interface() -> ApplicationProfilesInterface:
    return application_profiles_interface


ApplicationProfilesInterfaceDep = Annotated[
    ApplicationProfilesInterface, Depends(get_application_profiles_interface)
]
