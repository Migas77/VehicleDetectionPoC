from typing import Annotated

from fastapi import Depends

from app.drivers.sms.nef import nef_sms_interface
from app.interfaces.sms import SMSInterface

sms_interface: SMSInterface = nef_sms_interface


async def get_sms_interface() -> SMSInterface:
    return sms_interface


SMSInterfaceDep = Annotated[SMSInterface, Depends(get_sms_interface)]
