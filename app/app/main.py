import logging
from typing import cast, Iterable

from fastapi import FastAPI

import itertools

from app.drivers import router as drivers_router
from app.drivers.geofencing.deps import GeofencingInterfaceDep
from app.routers import router as routers_router
from app.drivers.analytics import AnalyticsInterfaceDep
from app.drivers.application_profiles import ApplicationProfilesInterfaceDep
from app.drivers.qod_provisioning import QoDProvisioningInterfaceDep
from app.drivers.qos_profiles import QoSProfilesInterfaceDep
from app.drivers.ues import UEsInterfaceDep
from app.interfaces import (
    AnalyticsInterface,
    ApplicationProfilesInterface,
    GeofencingInterface,
    QoDProvisioningInterface,
    QoSProfilesInterface,
)
from app.interfaces.ues import PocUEsByType, UEsInterface
from app.schemas.camara.common import Point
from app.schemas.poc import UE, PedestrianUE, SurveyedArea
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


async def _create_camera_analytics_setup(
    application_profiles_interface: ApplicationProfilesInterface,
    analytics_interface: AnalyticsInterface,
    camera_ues: list[CameraUE],
) -> list[str]:
    """Create an ApplicationProfile and analytics subscription for each camera UE."""
    subscription_ids: list[str] = []
    for camera in camera_ues:
        profile = await application_profiles_interface.create_application_profile(
            camera
        )
        sub_id = await analytics_interface.create_analytics_subscription(
            camera, profile.applicationProfileId
        )
        subscription_ids.append(sub_id)
    LOG.info("Analytics setup created for %d camera(s)", len(subscription_ids))
    return subscription_ids


async def _cleanup_camera_analytics_subscriptions(
    analytics_interface: AnalyticsInterface, camera_ues: list[CameraUE]
) -> None:
    """Delete every analytics subscription previously stored for each camera UE."""
    deleted = 0
    for camera in camera_ues:
        for sub_id in await analytics_interface.get_all_analytics_subscriptions(camera):
            await analytics_interface.delete_analytics_subscription(camera, sub_id)
            deleted += 1
    LOG.info("Analytics subscriptions deleted for camera UEs: %d", deleted)


def _build_camera_surveyed_area(camera: CameraUE) -> SurveyedArea | None:
    """Build the surveyed area for a camera from settings + its live location."""
    if camera.latitude is None or camera.longitude is None:
        LOG.warning(
            "Camera UE id=%s has no location, skipping geofencing area", camera.id
        )
        return None
    cfg = settings.cameras.get_area_by_ue_id(camera.id)
    if cfg is None:
        LOG.warning(
            "No surveyed area assignment for camera UE id=%s, using default", camera.id
        )
        cfg = settings.cameras.default_surveyed_area
    return SurveyedArea(
        camera_id=camera.id,
        center=Point(latitude=camera.latitude, longitude=camera.longitude),
        radius=cfg.radius,
        points=cfg.points,
    )


async def _create_pedestrian_geofencing_setup(
    geofencing_interface: GeofencingInterface,
    camera_ues: list[CameraUE],
    pedestrian_ues: list[PedestrianUE],
) -> None:
    """Create area-entered/left geofencing subscriptions for each pedestrian × camera."""
    count = 0
    for camera in camera_ues:
        area = _build_camera_surveyed_area(camera)
        if area is None:
            continue
        for pedestrian in pedestrian_ues:
            await geofencing_interface.create_geofencing_subscription(pedestrian, area)
            count += 1
    LOG.info("Geofencing subscriptions created for %d pedestrian-camera pair(s)", count)


async def _cleanup_pedestrian_geofencing(
    geofencing_interface: GeofencingInterface,
    camera_ues: list[CameraUE],
    pedestrian_ues: list[PedestrianUE],
) -> None:
    """Delete stored geofencing subscriptions per pedestrian and clear each camera's occupant set."""
    deleted = 0
    for pedestrian in pedestrian_ues:
        for sub_id in await geofencing_interface.get_all_geofencing_subscriptions(
            pedestrian
        ):
            await geofencing_interface.delete_geofencing_subscription(
                pedestrian, sub_id
            )
            deleted += 1
    for camera in camera_ues:
        await geofencing_interface.clear_camera_area_subscribers(camera.id)
    LOG.info("Geofencing subscriptions deleted: %d", deleted)


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
    analytics_interface: AnalyticsInterfaceDep,
    application_profiles_interface: ApplicationProfilesInterfaceDep,
    geofencing_interface: GeofencingInterfaceDep,
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

    await _create_camera_analytics_setup(
        application_profiles_interface, analytics_interface, camera_ues
    )

    pedestrian_ues = ues_by_type["pedestrian_ues"]
    # stale-cleanup any geofencing subscriptions/occupant sets from a previous run
    await _cleanup_pedestrian_geofencing(
        geofencing_interface, camera_ues, pedestrian_ues
    )
    await _create_pedestrian_geofencing_setup(
        geofencing_interface, camera_ues, pedestrian_ues
    )

    await _start_moving_ues(ues_interface, ues_by_type)

    return {"bootstrap": "OK"}


@app.post("/internal/cleanup")
async def cleanup_poc(
    analytics_interface: AnalyticsInterfaceDep,
    geofencing_interface: GeofencingInterfaceDep,
    qod_provisioning_interface: QoDProvisioningInterfaceDep,
    ues_interface: UEsInterfaceDep,
) -> dict[str, str]:
    # Shutdown
    ues_by_type = await ues_interface.get_poc_ues_by_type()
    await _stop_moving_ues(ues_interface, ues_by_type)

    camera_ues: list[CameraUE] = [
        *ues_by_type["static_camera_ues"],
        *ues_by_type["dynamic_camera_ues"],
    ]
    await _cleanup_camera_analytics_subscriptions(analytics_interface, camera_ues)
    await _cleanup_pedestrian_geofencing(
        geofencing_interface, camera_ues, ues_by_type["pedestrian_ues"]
    )

    deleted = 0
    for camera in camera_ues:
        provisioning_id = (
            await qod_provisioning_interface.retrieve_qod_provisioning_by_device(camera)
        )
        if provisioning_id is not None:
            await qod_provisioning_interface.delete_qod_provisioning(provisioning_id)
            deleted += 1
    LOG.info("QoD provisioning deleted for %d camera(s)", deleted)

    return {"cleanup": "OK"}
