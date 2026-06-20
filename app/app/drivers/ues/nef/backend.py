import logging

from pydantic import TypeAdapter

from app.interfaces.ues import PocUEsByType, UEsInterface
from app.schemas.poc import CarUE, DynamicCameraUE, PedestrianUE, PocUE, StaticCameraUE
from app.schemas.poc.ue import UE
from app.settings import settings

LOG = logging.getLogger(__name__)

_UEListAdapter: TypeAdapter[list[UE]] = TypeAdapter(list[UE])
_PocUEListAdapter: TypeAdapter[list[PocUE]] = TypeAdapter(list[PocUE])


class NefUEsBackend(UEsInterface):
    """Retrieves and classifies UEs from the NEF Emulator management API."""

    def __init__(self) -> None:
        self._client = settings.create_nef_auth_client()

    async def get_ues(self) -> list[UE]:
        res = await self._client.get("/api/v1/UEs")
        if not res.is_success:
            raise RuntimeError(
                f"Failed to fetch UEs from NEF ({res.status_code}): {res.text}"
            )
        return _UEListAdapter.validate_json(res.content)

    async def get_poc_ues(self) -> list[PocUE]:
        res = await self._client.get("/api/v1/UEs")
        if not res.is_success:
            raise RuntimeError(
                f"Failed to fetch UEs from NEF ({res.status_code}): {res.text}"
            )
        return _PocUEListAdapter.validate_json(res.content)

    async def get_poc_ues_by_type(self) -> PocUEsByType:
        ues = await self.get_poc_ues()
        return {
            "car_ues": [ue for ue in ues if isinstance(ue, CarUE)],
            "static_camera_ues": [ue for ue in ues if isinstance(ue, StaticCameraUE)],
            "dynamic_camera_ues": [ue for ue in ues if isinstance(ue, DynamicCameraUE)],
            "pedestrian_ues": [ue for ue in ues if isinstance(ue, PedestrianUE)],
        }
