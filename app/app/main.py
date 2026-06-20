import logging
from typing import cast, Iterable

from fastapi import FastAPI

import itertools

from app.drivers import router as drivers_router
from app.routers import router as routers_router
from app.drivers.qod_provisioning import QoDProvisioningInterfaceDep
from app.drivers.qos_profiles import QoSProfilesInterfaceDep
from app.drivers.ues import UEsInterfaceDep
from app.interfaces import QoDProvisioningInterface, QoSProfilesInterface
from app.interfaces.ues import PocUEsByType, UEsInterface
from app.schemas.poc import UE
from app.schemas.poc.cameras import CameraUE
from app.settings import settings

LOG = logging.getLogger(__name__)


async def _verify_camera_qos_profiles(
    qos_profiles_interface: QoSProfilesInterface, camera_ues: list[CameraUE]
) -> None:
    """Verify the QoS profile for each camera UE is active and matches the configured spec."""
    if not camera_ues:
        raise RuntimeError("No camera UEs provided for QoS profile verification")

    for camera in camera_ues:
        valid = await qos_profiles_interface.verify_qos_profile(camera)
        if not valid:
            raise RuntimeError(
                f"QoS profile verification failed for camera UE '{camera.name}' (id={camera.id})"
            )

    LOG.info("QoS profile verification passed for %d camera(s)", len(camera_ues))


async def _cleanup_stale_camera_qod_provisioning(
    qod_provisioning_interface: QoDProvisioningInterface, camera_ues: list[CameraUE]
) -> None:
    """Delete any pre-existing QoD provisioning for each camera UE before assigning new ones."""
    for camera in camera_ues:
        provisioning_id = (
            await qod_provisioning_interface.retrieve_qod_provisioning_by_device(camera)
        )
        if provisioning_id is not None:
            LOG.warning(
                "Stale QoD provisioning found for camera UE id=%s (provisioningId=%s), deleting",
                camera.id,
                provisioning_id,
            )
            await qod_provisioning_interface.delete_qod_provisioning(provisioning_id)


async def _assign_camera_qos_provisioning(
    qod_provisioning_interface: QoDProvisioningInterface, camera_ues: list[CameraUE]
) -> list[str]:
    """Create QoD provisioning for each camera UE and return the list of provisioning IDs."""
    provisioning_ids: list[str] = []
    for camera in camera_ues:
        provisioning_id = await qod_provisioning_interface.assign_qos_profile(camera)
        provisioning_ids.append(provisioning_id)
    return provisioning_ids


async def _start_moving_ues(
    ues_interface: UEsInterface, ues_by_type: PocUEsByType
) -> None:
    """Start the movement loop for all car, dynamic camera, and pedestrian UEs."""
    for ue in itertools.chain(
        cast(Iterable[UE], ues_by_type["car_ues"]),
        cast(Iterable[UE], ues_by_type["dynamic_camera_ues"]),
        cast(Iterable[UE], ues_by_type["pedestrian_ues"]),
    ):
        await ues_interface.start_movement(ue.supi)


async def _stop_moving_ues(
    ues_interface: UEsInterface, ues_by_type: PocUEsByType
) -> None:
    """Stop the movement loop for all car, dynamic camera, and pedestrian UEs."""
    for ue in itertools.chain(
        cast(Iterable[UE], ues_by_type["car_ues"]),
        cast(Iterable[UE], ues_by_type["dynamic_camera_ues"]),
        cast(Iterable[UE], ues_by_type["pedestrian_ues"]),
    ):
        await ues_interface.stop_movement(ue.supi)


app = FastAPI(title=settings.poc_title)
app.include_router(drivers_router)
app.include_router(routers_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"health": "OK"}


@app.post("/internal/bootstrap")
async def bootstrap_poc(
    qod_provisioning_interface: QoDProvisioningInterfaceDep,
    qos_profiles_interface: QoSProfilesInterfaceDep,
    ues_interface: UEsInterfaceDep,
) -> dict[str, str]:
    # Startup
    profiles = await qos_profiles_interface.get_qos_profiles()
    LOG.info("Available QoS profiles: %s", profiles)

    ues_by_type = await ues_interface.get_poc_ues_by_type()
    LOG.info(
        "Fetched UEs from NEF: %d cars, %d cameras (%d static, %d dynamic), %d pedestrians",
        len(ues_by_type["car_ues"]),
        len(ues_by_type["static_camera_ues"]) + len(ues_by_type["dynamic_camera_ues"]),
        len(ues_by_type["static_camera_ues"]),
        len(ues_by_type["dynamic_camera_ues"]),
        len(ues_by_type["pedestrian_ues"]),
    )

    camera_ues: list[CameraUE] = [
        *ues_by_type["static_camera_ues"],
        *ues_by_type["dynamic_camera_ues"],
    ]
    await _verify_camera_qos_profiles(qos_profiles_interface, camera_ues)
    await _cleanup_stale_camera_qod_provisioning(qod_provisioning_interface, camera_ues)
    provisioning_ids = await _assign_camera_qos_provisioning(
        qod_provisioning_interface, camera_ues
    )
    LOG.info("QoD provisioning created for %d camera(s)", len(provisioning_ids))

    await _start_moving_ues(ues_interface, ues_by_type)

    return {"bootstrap": "OK"}


@app.post("/internal/cleanup")
async def cleanup_poc(
    qod_provisioning_interface: QoDProvisioningInterfaceDep,
    ues_interface: UEsInterfaceDep,
) -> dict[str, str]:
    ues_by_type = await ues_interface.get_poc_ues_by_type()
    await _stop_moving_ues(ues_interface, ues_by_type)

    deleted = 0
    for camera in itertools.chain(
        ues_by_type["static_camera_ues"], ues_by_type["dynamic_camera_ues"]
    ):
        provisioning_id = (
            await qod_provisioning_interface.retrieve_qod_provisioning_by_device(camera)
        )
        if provisioning_id is not None:
            await qod_provisioning_interface.delete_qod_provisioning(provisioning_id)
            deleted += 1

    LOG.info("QoD provisioning deleted for %d camera(s)", deleted)

    return {"cleanup": "OK"}
