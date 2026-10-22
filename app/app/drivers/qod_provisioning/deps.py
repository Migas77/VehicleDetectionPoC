from typing import Annotated

from fastapi import Depends

from app.interfaces.qod_provisioning import QoDProvisioningInterface


def get_qod_provisioning_interface() -> QoDProvisioningInterface:
    # Imported lazily to avoid a circular import: the package __init__ imports the
    # callbacks (which import this Dep) while still wiring up `qod_provisioning_interface`.
    from app.drivers.qod_provisioning import qod_provisioning_interface

    return qod_provisioning_interface


QoDProvisioningInterfaceDep = Annotated[
    QoDProvisioningInterface, Depends(get_qod_provisioning_interface)
]
