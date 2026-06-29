import asyncio
import functools
import logging
from datetime import timedelta
from typing import Any
from uuid import UUID, uuid4

import redis.asyncio as aioredis
from fastapi import APIRouter
from fastapi.responses import Response

from geopy.geocoders import Nominatim

from app.drivers.crash_status import CrashStatusBrokerDep
from app.interfaces.crash_status import CrashStatusBrokerInterface
from app.drivers.ccam import CcamInterfaceDep
from app.drivers.geofencing.deps import GeofencingInterfaceDep
from app.drivers.location import LocationInterfaceDep
from app.drivers.sms import SMSInterfaceDep
from app.drivers.ues import UEsInterfaceDep
from app.interfaces.ccam import CcamInterface
from app.interfaces.geofencing import GeofencingInterface
from app.interfaces.location import LocationInterface
from app.interfaces.sms import SMSInterface
from app.interfaces.ues import UEsInterface
from app.redis import RedisDep
from app.schemas.camara.location import Circle
from app.schemas.poc.crash_status import (
    CrashLocation,
    CrashNotificationChannel,
    CrashNotificationStatus,
    CrashStatusEvent,
)
from app.settings import settings

LOG = logging.getLogger(__name__)

router = APIRouter(prefix="/callbacks/crash_inference")

_DEBOUNCE_KEY_PREFIX = "poc:crash_inference:debounce:"
_STREAK_KEY_PREFIX = "poc:crash_inference:streak:"

_CRASH_ALERT_SMS = "ALERT: Vehicle crash detected nearby. Please be cautious."


@functools.lru_cache(maxsize=512)
def _fetch_road_name(lat: float, lon: float) -> str | None:
    geolocator = Nominatim(user_agent="vehicle-detection-poc")
    result = geolocator.reverse((lat, lon), language="en")
    return (result.raw.get("address") or {}).get("road") if result else None


async def _get_road_name(lat: float, lon: float) -> str | None:
    key = (round(lat, 4), round(lon, 4))
    try:
        return await asyncio.to_thread(_fetch_road_name, *key)
    except Exception:
        LOG.exception("Reverse geocoding failed for (%s, %s)", lat, lon)
        return None


@router.post("/{ue_supi}", status_code=204)
async def crash_inference_webhook(
    ue_supi: str,
    body: dict[str, Any],
    redis: RedisDep,
    ues: UEsInterfaceDep,
    sms: SMSInterfaceDep,
    ccam: CcamInterfaceDep,
    geofencing: GeofencingInterfaceDep,
    location: LocationInterfaceDep,
    broker: CrashStatusBrokerDep,
) -> Response:
    """Receive Roboflow inference webhook. Returns 204 immediately; processing runs in background."""
    asyncio.create_task(
        _process_detection(
            ue_supi, body, redis, ues, sms, ccam, geofencing, location, broker
        )
    )
    return Response(status_code=204)


async def _process_detection(
    ue_supi: str,
    payload: dict[str, Any],
    redis: aioredis.Redis,
    ues: UEsInterface,
    sms: SMSInterface,
    ccam: CcamInterface,
    geofencing: GeofencingInterface,
    location: LocationInterface,
    broker: CrashStatusBrokerInterface,
) -> None:

    detections_number: int = payload.get("detections_number", 0)
    frame_number = payload.get("frame_number")
    LOG.info(
        "Processing inference result: detections=%s, frame=%s, all=%s",
        detections_number,
        frame_number,
        payload,
    )

    streak_key = f"{_STREAK_KEY_PREFIX}{ue_supi}"
    if frame_number is None:
        LOG.error(
            "Inference payload for camera supi=%s has no frame_number",
            ue_supi,
        )
        return
    if detections_number == 0:
        await redis.delete(streak_key)
        return

    predictions: list[dict[str, Any]] = (payload.get("predictions") or {}).get(
        "predictions"
    ) or []
    matching = [
        p
        for p in predictions
        if (p.get("class") or "").lower() in settings.crash_inference.classes
        and p.get("confidence", 0.0) >= settings.crash_inference.intervention_threshold
    ]
    if not matching:
        await redis.delete(streak_key)
        return

    debounce_key = f"{_DEBOUNCE_KEY_PREFIX}{ue_supi}"
    if await redis.exists(debounce_key):
        LOG.debug(
            "Intervention debounced for camera supi=%s on frame %s (debounce=%.1fs)",
            ue_supi,
            frame_number,
            settings.crash_inference.debounce_seconds,
        )
        return

    # Require the crash detection to persist across crash_window_size frames
    max_fps = settings.cameras.get_inference_config_by_ue_supi(ue_supi).max_fps
    required_span = settings.crash_inference.crash_window_size(max_fps)
    first_frame = await redis.get(streak_key)
    if first_frame is None:
        await redis.set(streak_key, frame_number)
        return
    span = frame_number - int(first_frame)
    if span < required_span:
        return

    # Detection persisted across x frames
    # Redis reset + crash detection notification to UEs
    await redis.set(
        debounce_key,
        "1",
        ex=timedelta(seconds=settings.crash_inference.debounce_seconds),
    )
    await redis.delete(streak_key)
    LOG.warning(
        "Intervention triggered: crash persisted across frames %s..%s (span %d >= %d) "
        "for camera supi=%s (classes=%s)",
        first_frame,
        frame_number,
        span,
        required_span,
        ue_supi,
        [p["class"] for p in matching],
    )

    crash_location: CrashLocation | None = None
    try:
        camera_ue = await ues.get_ue_by_supi(ue_supi)
        camera_loc = await location.retrieve_location(camera_ue)
        area = camera_loc.area
        if not isinstance(area, Circle):
            raise RuntimeError(
                f"Unsupported location area type {type(area).__name__} for camera supi={ue_supi}"
            )
        road_name = await _get_road_name(area.center.latitude, area.center.longitude)
        crash_location = CrashLocation(
            latitude=area.center.latitude,
            longitude=area.center.longitude,
            road_name=road_name,
        )
    except Exception:
        LOG.exception("Failed to fetch camera location for supi=%s", ue_supi)

    incident_id = uuid4()
    await broker.publish(
        CrashStatusEvent(
            incident_id=incident_id,
            camera_supi=ue_supi,
            status=CrashNotificationStatus.detected,
            location=crash_location,
        )
    )

    # Crash detection handling - Send SMS to nearby pedestrian UEs
    await _send_crash_sms_to_nearby_pedestrians(
        ue_supi, geofencing, ues, sms, incident_id, broker, crash_location
    )

    # Crash detection handling - Send DENM message to nearby vehicle UEs
    await _send_crash_denm_to_nearby_vehicles(
        ue_supi, ccam, crash_location, incident_id, broker
    )


async def _send_crash_sms_to_nearby_pedestrians(
    camera_supi: str,
    geofencing: GeofencingInterface,
    ues: UEsInterface,
    sms: SMSInterface,
    incident_id: UUID,
    broker: CrashStatusBrokerInterface,
    crash_location: CrashLocation | None,
) -> None:
    nearby_supis = await geofencing.get_camera_area_subscribers(camera_supi)
    if not nearby_supis:
        LOG.info(
            "No nearby UEs in camera supi=%s area, skipping SMS notifications",
            camera_supi,
        )
        return

    await asyncio.gather(
        *[
            _fetch_ue_and_send_sms(
                supi, ues, sms, camera_supi, incident_id, broker, crash_location
            )
            for supi in nearby_supis
        ]
    )


async def _fetch_ue_and_send_sms(
    supi: str,
    ues: UEsInterface,
    sms: SMSInterface,
    camera_supi: str,
    incident_id: UUID,
    broker: CrashStatusBrokerInterface,
    crash_location: CrashLocation | None,
) -> None:
    try:
        ue = await ues.get_ue_by_supi(supi)
    except Exception:
        LOG.exception("Failed to fetch UE supi=%s for SMS notification", supi)
        return

    try:
        await sms.send_sms(ue, _CRASH_ALERT_SMS)
        await broker.publish(
            CrashStatusEvent(
                incident_id=incident_id,
                camera_supi=camera_supi,
                status=CrashNotificationStatus.notified,
                channel=CrashNotificationChannel.sms,
                recipient=supi,
                location=crash_location,
            )
        )
    except Exception:
        LOG.exception("Failed to send SMS to UE supi=%s", supi)


async def _send_crash_denm_to_nearby_vehicles(
    camera_supi: str,
    ccam: CcamInterface,
    crash_location: CrashLocation | None,
    incident_id: UUID,
    broker: CrashStatusBrokerInterface,
) -> None:
    if crash_location is None:
        LOG.warning(
            "Skipping DENM for camera supi=%s: location unavailable", camera_supi
        )
        return
    try:
        await ccam.send_denm(crash_location)
        await broker.publish(
            CrashStatusEvent(
                incident_id=incident_id,
                camera_supi=camera_supi,
                status=CrashNotificationStatus.notified,
                channel=CrashNotificationChannel.denm,
                location=crash_location,
            )
        )
    except Exception:
        LOG.exception("Failed to send DENM for camera supi=%s", camera_supi)
