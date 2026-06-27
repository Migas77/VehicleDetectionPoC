import logging
from datetime import datetime
from functools import cached_property
from ipaddress import IPv4Address
from typing import Any

import httpx
from pydantic import AnyUrl, TypeAdapter

from app.interfaces.location import LocationInterface
from app.schemas.camara.common import Point as CamaraPoint
from app.schemas.camara.location import Circle, Location, Polygon
from app.schemas.nef.monitoringevent import (
    MonitoringEventSubscription,
    MonitoringType,
)
from app.schemas.poc.ue import UE
from app.settings import settings

LOG = logging.getLogger(__name__)

_dict_adapter: TypeAdapter[dict[str, Any]] = TypeAdapter(dict[str, Any])

_DUMMY_NOTIFICATION_DEST: AnyUrl = AnyUrl("https://0.0.0.0")
_POINT_DEFAULT_RADIUS = 10.0  # metres — used when the NEF returns a point shape


class NefLocationBackend(LocationInterface):
    """Retrieves UE location via a one-shot NEF MonitoringEvent LOCATION_REPORTING subscription."""

    @cached_property
    def _client(self) -> httpx.AsyncClient:
        return settings.create_nef_auth_client()

    async def retrieve_location(self, ue: UE) -> Location:
        if ue.ip_address_v4 is not None:
            payload = MonitoringEventSubscription(
                monitoringType=MonitoringType.LOCATION_REPORTING,
                notificationDestination=_DUMMY_NOTIFICATION_DEST,
                maximumNumberOfReports=1,
                ipv4Addr=IPv4Address(ue.ip_address_v4),
            )
        elif ue.msisdn is not None:
            payload = MonitoringEventSubscription(
                monitoringType=MonitoringType.LOCATION_REPORTING,
                notificationDestination=_DUMMY_NOTIFICATION_DEST,
                maximumNumberOfReports=1,
                msisdn=ue.msisdn,
            )
        else:
            raise ValueError(
                f"Cannot identify UE supi={ue.supi} for NEF: "
                "neither ip_address_v4 nor msisdn is set"
            )

        url = f"/nef/api/v1/3gpp-monitoring-event/v1/{settings.poc_af_id}/subscriptions"
        res = await self._client.post(
            url,
            content=payload.model_dump_json(exclude_unset=True),
            headers={"Content-Type": "application/json"},
        )
        if not res.is_success:
            raise RuntimeError(
                f"NEF location retrieval failed ({res.status_code}): {res.text}"
            )
        data = _dict_adapter.validate_json(res.content)
        location = self._parse_location(data, ue.supi)
        return location

    @staticmethod
    def _parse_location(data: dict[str, Any], ue_supi: str) -> Location:
        """Map a NEF MonitoringEvent subscription response to a CAMARA Location."""
        location_info = data.get("locationInfo")
        if location_info is None:
            raise RuntimeError(
                f"NEF response missing 'locationInfo' for UE supi={ue_supi}"
            )

        area = location_info.get("geographicArea")
        if area is None:
            raise RuntimeError(
                f"NEF response missing 'locationInfo.geographicArea' for UE supi={ue_supi}"
            )

        shape = area.get("shape")

        if shape == "POINT":
            point = area["point"]
            return Location(
                lastLocationTime=datetime.now(),
                area=Circle(
                    center=CamaraPoint(latitude=point["lat"], longitude=point["lon"]),
                    radius=_POINT_DEFAULT_RADIUS,
                ),
            )

        if shape == "POLYGON":
            return Location(
                lastLocationTime=datetime.now(),
                area=Polygon(boundary=area["pointList"]),
            )

        raise RuntimeError(
            f"Unsupported NEF geographicArea shape '{shape}' for UE supi={ue_supi}"
        )
