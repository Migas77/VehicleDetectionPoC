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

    async def get_ue_by_supi(self, supi: str) -> UE:
        res = await self._client.get(f"/api/v1/UEs/{supi}")
        if res.status_code == 404:
            raise RuntimeError(f"UE supi={supi} not found in NEF")
        if not res.is_success:
            raise RuntimeError(
                f"Failed to fetch UE supi={supi} from NEF ({res.status_code}): {res.text}"
            )
        return UE.model_validate_json(res.content)

    async def start_movement(self, supi: str) -> bool:
        LOG.info("Starting movement loop for UE supi=%s", supi)
        res = await self._client.post(
            "/api/v1/ue_movement/start-loop", json={"supi": supi}
        )
        if res.status_code == 409:
            LOG.warning("Movement loop already started for UE supi=%s", supi)
            return True
        if not res.is_success:
            raise RuntimeError(
                f"Failed to start movement loop for supi={supi} ({res.status_code}): {res.text}"
            )
        LOG.info("Movement loop started for UE supi=%s", supi)
        return True

    async def stop_movement(self, supi: str) -> bool:
        LOG.info("Stopping movement loop for UE supi=%s", supi)
        res = await self._client.post(
            "/api/v1/ue_movement/stop-loop", json={"supi": supi}
        )
        if res.status_code == 409:
            LOG.info("Movement loop not running for UE supi=%s, nothing to stop", supi)
            return True
        if not res.is_success:
            raise RuntimeError(
                f"Failed to stop movement loop for supi={supi} ({res.status_code}): {res.text}"
            )
        LOG.info("Movement loop stopped for UE supi=%s", supi)
        return True
