import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from pydantic import TypeAdapter

from app.drivers import router as drivers_router
from app.drivers.qos_profiles import qos_profiles_interface
from app.schemas.poc import StaticCameraUE, DynamicCameraUE, CarUE, PedestrianUE
from app.schemas.poc.cameras import CameraUE
from app.schemas.poc.poc_ue import PocUE
from app.settings import settings

LOG = logging.getLogger(__name__)


async def _verify_camera_qos_profiles() -> None:
    """Fetch all UEs from the NEF, find cameras, and verify their QoS profiles are active."""
    async with settings.create_nef_auth_client() as client:
        res = await client.get("/api/v1/UEs")
        if not res.is_success:
            raise RuntimeError(
                f"Failed to fetch UEs from NEF ({res.status_code}): {res.text}"
            )

        ues = TypeAdapter(list[PocUE]).validate_json(res.content)
        car_ues = [ue for ue in ues if isinstance(ue, CarUE)]
        camera_ues = [ue for ue in ues if isinstance(ue, CameraUE)]
        static_camera_ues = [ue for ue in camera_ues if isinstance(ue, StaticCameraUE)]
        dynamic_camera_ues = [
            ue for ue in camera_ues if isinstance(ue, DynamicCameraUE)
        ]
        pedestrian_ues = [ue for ue in ues if isinstance(ue, PedestrianUE)]

        LOG.info(
            "Fetched %d UEs from NEF: %d cars, %d cameras (%d static, %d dynamic), %d pedestrians",
            len(ues),
            len(car_ues),
            len(camera_ues),
            len(static_camera_ues),
            len(dynamic_camera_ues),
            len(pedestrian_ues),
        )

        if not camera_ues:
            raise RuntimeError(
                "No camera UEs found in NEF — skipping QoS profile verification"
            )

        for camera in camera_ues:
            valid = await qos_profiles_interface.verify_qos_profile(camera)
            if not valid:
                raise RuntimeError(
                    f"QoS profile verification failed for camera UE '{camera.name}' (id={camera.id})"
                )
        LOG.info("QoS profile verification passed for %d camera(s)", len(camera_ues))


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    profiles = await qos_profiles_interface.get_qos_profiles()
    LOG.info("Available QoS profiles: %s", profiles)
    await _verify_camera_qos_profiles()
    yield


app = FastAPI(title=settings.poc_title, lifespan=lifespan)
app.include_router(drivers_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}
