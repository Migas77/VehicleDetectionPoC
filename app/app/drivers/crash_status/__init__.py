from typing import Annotated

from fastapi import Depends

from app.drivers.crash_status.backend import AsyncioCrashStatusBroker
from app.interfaces.crash_status import CrashStatusBrokerInterface

crash_status_broker: CrashStatusBrokerInterface = AsyncioCrashStatusBroker()


def get_crash_status_broker() -> CrashStatusBrokerInterface:
    return crash_status_broker


CrashStatusBrokerDep = Annotated[
    CrashStatusBrokerInterface, Depends(get_crash_status_broker)
]
