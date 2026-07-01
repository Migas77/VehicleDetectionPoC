import itertools
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import cast, Iterable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.drivers import router as drivers_router
from app.drivers.analytics import AnalyticsInterfaceDep
from app.drivers.application_profiles import ApplicationProfilesInterfaceDep
from app.drivers.crash_inference import CrashInferenceInterfaceDep
from app.drivers.geofencing.deps import GeofencingInterfaceDep
from app.drivers.qod_provisioning import QoDProvisioningInterfaceDep
from app.drivers.qos_profiles import QoSProfilesInterfaceDep
from app.drivers.ues import UEsInterfaceDep
from app.interfaces import (
    AnalyticsInterface,
    ApplicationProfilesInterface,
    CrashInferenceInterface,
    GeofencingInterface,
    QoDProvisioningInterface,
    QoSProfilesInterface,
)
from app.mqtt import mqtt_lifespan
from app.routers import router as routers_router
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
                f"QoS profile verification failed for camera UE '{camera.name}' (supi={camera.supi})"
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
                "Stale QoD provisioning found for camera UE supi=%s (provisioningId=%s), deleting",
                camera.supi,
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
            "Camera UE supi=%s has no location, skipping geofencing area", camera.supi
        )
        return None
    cfg = settings.cameras.get_area_by_ue_supi(camera.supi)
    if cfg is None:
        LOG.warning(
            "No surveyed area assignment for camera UE supi=%s, using default",
            camera.supi,
        )
        cfg = settings.cameras.default_surveyed_area
    return SurveyedArea(
        camera_supi=camera.supi,
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
        await geofencing_interface.clear_camera_area_subscribers(camera.supi)
    LOG.info("Geofencing subscriptions deleted: %d", deleted)


async def _start_camera_inference_pipelines(
    crash_inference_interface: CrashInferenceInterface,
    camera_ues: list[CameraUE],
) -> None:
    """Start crash inference pipelines for all inference-enabled camera UEs."""
    started = 0
    for camera in camera_ues:
        pipeline_id = await crash_inference_interface.start_pipeline(camera)
        if pipeline_id is not None:
            started += 1
    LOG.info("Crash inference pipelines started for %d camera(s)", started)


async def _terminate_camera_inference_pipelines(
    crash_inference_interface: CrashInferenceInterface,
    camera_ues: list[CameraUE],
) -> None:
    """Terminate crash inference pipelines for all camera UEs."""
    for camera in camera_ues:
        await crash_inference_interface.terminate_pipeline(camera)
    LOG.info("Crash inference pipelines terminated for %d camera(s)", len(camera_ues))


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


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    if settings.ccam_broker.backend == "mqtt":
        async with mqtt_lifespan():
            yield
    else:
        yield


app = FastAPI(title=settings.poc_title, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
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

    return {"internal_boostrap": "OK"}


@app.post("/internal/cleanup")
async def cleanup_poc(
    analytics_interface: AnalyticsInterfaceDep,
    geofencing_interface: GeofencingInterfaceDep,
    qod_provisioning_interface: QoDProvisioningInterfaceDep,
    ues_interface: UEsInterfaceDep,
) -> dict[str, str]:
    # Shutdown
    ues_by_type = await ues_interface.get_poc_ues_by_type()
    camera_ues: list[CameraUE] = [
        *ues_by_type["static_camera_ues"],
        *ues_by_type["dynamic_camera_ues"],
    ]
    await _stop_moving_ues(ues_interface, ues_by_type)

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

    return {"internal_cleanup": "OK"}


@app.post("/inference/bootstrap")
async def bootstrap_inference(
    crash_inference_interface: CrashInferenceInterfaceDep,
    ues_interface: UEsInterfaceDep,
) -> dict[str, str]:
    ues_by_type = await ues_interface.get_poc_ues_by_type()
    camera_ues: list[CameraUE] = [
        *ues_by_type["static_camera_ues"],
        *ues_by_type["dynamic_camera_ues"],
    ]
    await _start_camera_inference_pipelines(crash_inference_interface, camera_ues)
    return {"inference_bootstrap": "OK"}


@app.post("/inference/cleanup")
async def cleanup_inference(
    crash_inference_interface: CrashInferenceInterfaceDep,
    ues_interface: UEsInterfaceDep,
) -> dict[str, str]:
    ues_by_type = await ues_interface.get_poc_ues_by_type()
    camera_ues: list[CameraUE] = [
        *ues_by_type["static_camera_ues"],
        *ues_by_type["dynamic_camera_ues"],
    ]
    await _terminate_camera_inference_pipelines(crash_inference_interface, camera_ues)
    return {"inference_cleanup": "OK"}
