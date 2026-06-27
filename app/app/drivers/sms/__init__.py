from typing import Annotated

from fastapi import Depends

from app.interfaces.sms import SMSInterface
from app.settings import settings

sms_interface: SMSInterface

match settings.net_apis.api:
    case "nef":
        from .nef import nef_sms_interface

        sms_interface = nef_sms_interface
    case "camara":
        raise RuntimeError(
            "SMS sending is not supported in CAMARA mode: "
            "the CAMARA gateway does not expose a generic SMS API"
        )


async def get_sms_interface() -> SMSInterface:
    return sms_interface


SMSInterfaceDep = Annotated[SMSInterface, Depends(get_sms_interface)]
