import asyncio
import logging
from typing import Optional

from fastapi import APIRouter, WebSocket
from pydantic import TypeAdapter
from starlette.websockets import WebSocketDisconnect

from app.drivers.location import LocationInterfaceDep
from app.drivers.ues import UEsInterfaceDep
from app.interfaces.location import LocationInterface

from app.schemas.poc import CarUE, DynamicCameraUE, PedestrianUE, PocUE, StaticCameraUE
from app.schemas.poc.ue_location import UELocation, UEType

LOG = logging.getLogger(__name__)
router = APIRouter()

_ue_location_list_adapter: TypeAdapter[list[UELocation]] = TypeAdapter(list[UELocation])


def _ue_type(ue: PocUE) -> UEType:
    if isinstance(ue, CarUE):
        return UEType.car
    if isinstance(ue, (StaticCameraUE, DynamicCameraUE)):
        return UEType.camera
    if isinstance(ue, PedestrianUE):
        return UEType.pedestrian
    raise ValueError(f"cannot determine UE type for UE supi={ue.supi}")


async def _ue_location_entry(
    ue: PocUE, location_interface: LocationInterface
) -> Optional[UELocation]:
    try:
        loc = await location_interface.retrieve_location(ue)
        return UELocation(ue=ue, type=_ue_type(ue), location=loc)
    except (RuntimeError, ValueError) as exc:
        LOG.warning("Location unavailable for UE %s (%s): %s", ue.supi, ue.msisdn, exc)
        return None


@router.websocket("/location")
async def stream_ue_locations(
    websocket: WebSocket,
    ue_interface: UEsInterfaceDep,
    location_interface: LocationInterfaceDep,
) -> None:
    await websocket.accept()

    try:
        while True:
            await asyncio.sleep(0.5)

            ues = await ue_interface.get_poc_ues()
            if not ues:
                continue

            results = await asyncio.gather(
                *(_ue_location_entry(ue, location_interface) for ue in ues),
                return_exceptions=True,
            )

            locations = [r for r in results if isinstance(r, UELocation)]
            await websocket.send_text(
                _ue_location_list_adapter.dump_json(locations).decode()
            )

    except WebSocketDisconnect:
        LOG.info("WebSocket client disconnected")
