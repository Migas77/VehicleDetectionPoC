import logging

import geopy.distance
from fastapi import APIRouter
from shapely import Point as ShapelyPoint

from app.drivers.geofencing.deps import GeofencingInterfaceDep
from app.interfaces.geofencing import GeofencingInterface
from app.redis import RedisDep
from app.schemas.nef.monitoringevent import MonitoringNotification, SupportedGADShapes
from app.schemas.poc.area import SurveyedArea
from app.schemas.poc.geofencing import GeofenceState, ManagedGeofencingSubscription

LOG = logging.getLogger(__name__)

router = APIRouter()


@router.post("/nef/{ue_id}/{camera_id}/{subscription_id}")
async def nef_geofencing_callback(
    ue_id: int,
    camera_id: int,
    subscription_id: str,
    body: MonitoringNotification,
    geofencing_interface: GeofencingInterfaceDep,
    redis: RedisDep,
) -> None:
    """Receive NEF LOCATION_REPORTING notifications and compute geofence enter/leave."""
    if not body.monitoringEventReports:
        LOG.warning(
            "NEF geofencing callback for UE id=%s, sub=%s: no monitoring event reports",
            ue_id,
            subscription_id,
        )
        return
    report = body.monitoringEventReports[0]
    if report.locationInfo is None or report.locationInfo.geographicArea is None:
        LOG.warning(
            "NEF geofencing callback for UE id=%s, sub=%s: no location info",
            ue_id,
            subscription_id,
        )
        return
    geographic_area = report.locationInfo.geographicArea
    if geographic_area.shape != SupportedGADShapes.POINT:
        LOG.warning(
            "NEF geofencing callback for UE id=%s, sub=%s: unsupported shape %s",
            ue_id,
            subscription_id,
            geographic_area.shape,
        )
        return
    coordinates = geographic_area.point

    key = GeofencingInterface.subscription_key(ue_id, subscription_id)
    raw = await redis.get(key)
    if raw is None:
        LOG.warning(
            "NEF geofencing callback: no managed subscription for UE id=%s, sub=%s",
            ue_id,
            subscription_id,
        )
        return

    managed = ManagedGeofencingSubscription.model_validate_json(raw)
    inside = _is_inside(managed.area, coordinates.lat, coordinates.lon)
    new_state = GeofenceState.INSIDE if inside else GeofenceState.OUTSIDE
    if managed.last_state == new_state:
        return  # no transition

    if new_state == GeofenceState.INSIDE:
        await geofencing_interface.register_in_camera_area(camera_id, ue_id)
        LOG.info("UE id=%s entered camera id=%s area (NEF)", ue_id, camera_id)
    elif managed.last_state == GeofenceState.INSIDE:
        # genuine INSIDE -> OUTSIDE transition
        await geofencing_interface.unregister_from_camera_area(camera_id, ue_id)
        LOG.info("UE id=%s left camera id=%s area (NEF)", ue_id, camera_id)

    managed.last_state = new_state
    await redis.set(key, managed.model_dump_json())


def _is_inside(area: SurveyedArea, lat: float, lon: float) -> bool:
    """Return True if the (lat, lon) point falls inside the surveyed area."""
    polygon = area.polygon
    if polygon is not None:
        return bool(polygon.contains(ShapelyPoint(lon, lat)))
    center = (area.center.latitude, area.center.longitude)
    distance_m = geopy.distance.geodesic(center, (lat, lon)).m
    return bool(distance_m < area.radius)
