from typing import Annotated

from fastapi import Depends

from app.interfaces.geofencing import GeofencingInterface


def get_geofencing_interface() -> GeofencingInterface:
    # Imported lazily to avoid a circular import: the package __init__ imports the
    # callbacks (which import this Dep) while still wiring up `geofencing_interface`.
    from app.drivers.geofencing import geofencing_interface

    return geofencing_interface


GeofencingInterfaceDep = Annotated[
    GeofencingInterface, Depends(get_geofencing_interface)
]
