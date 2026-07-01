import logging

from fastapi import APIRouter, HTTPException

from app.schemas.poc.cameras import CameraInfo
from app.settings import settings

LOG = logging.getLogger(__name__)

router = APIRouter(prefix="/cameras")


@router.get("")
async def list_cameras() -> list[CameraInfo]:
    """List the full configuration of every camera declared in cameras.toml."""
    return [_camera_info(supi) for supi in sorted(_camera_supis())]


@router.get("/{ue_supi}")
async def get_camera(ue_supi: str) -> CameraInfo:
    """Get the full configuration of a single camera by its UE supi."""
    if ue_supi not in _camera_supis():
        raise HTTPException(status_code=404, detail=f"Unknown camera supi={ue_supi}")
    return _camera_info(ue_supi)


def _camera_supis() -> set[str]:
    camera_supis = (
        set(settings.cameras.qos_profiles_assignment)
        | set(settings.cameras.surveyed_areas)
        | set(settings.cameras.inference)
    )
    camera_supis.discard("default")
    return camera_supis


def _camera_info(ue_supi: str) -> CameraInfo:
    return CameraInfo(
        ue_supi=ue_supi,
        qos_profile=settings.cameras.get_by_ue_supi(ue_supi)
        or settings.cameras.default_qos_profile,
        surveyed_area=settings.cameras.get_area_by_ue_supi(ue_supi)
        or settings.cameras.default_surveyed_area,
        inference=settings.cameras.get_inference_config_by_ue_supi(ue_supi),
    )
