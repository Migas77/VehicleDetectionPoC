import logging

from fastapi import APIRouter, HTTPException

from app.schemas.poc.cameras import CameraInfo, SurveyedAreaOut
from app.settings import SurveyedAreaConfig, settings

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
    area_cfg = (
        settings.cameras.get_area_by_ue_supi(ue_supi)
        or settings.cameras.default_surveyed_area
    )
    return CameraInfo(
        ue_supi=ue_supi,
        qos_profile=settings.cameras.get_by_ue_supi(ue_supi)
        or settings.cameras.default_qos_profile,
        surveyed_area=_resolve_surveyed_area(area_cfg),
        inference=settings.cameras.get_inference_config_by_ue_supi(ue_supi),
    )


def _resolve_surveyed_area(cfg: SurveyedAreaConfig) -> SurveyedAreaOut:
    """Resolve the surveyed-area shape actually enforced by the active net_apis backend.

    The CAMARA backend only ever sends a Circle (radius), ignoring any configured points.
    The NEF backend refines into the polygon (points) when configured, falling back to
    the circle (radius) otherwise — see app/drivers/geofencing/nef/callbacks.py::_is_inside.
    """
    if settings.net_apis.api == "camara":
        return SurveyedAreaOut(radius=cfg.radius)
    if cfg.points:
        return SurveyedAreaOut(points=cfg.points)
    return SurveyedAreaOut(radius=cfg.radius)
