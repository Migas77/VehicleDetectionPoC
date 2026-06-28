from datetime import datetime, timezone
from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class CrashNotificationStatus(str, Enum):
    detected = "DETECTED"
    notified = "NOTIFIED"


class CrashNotificationChannel(str, Enum):
    sms = "SMS"
    denm = "DENM"


class CrashLocation(BaseModel):
    latitude: float
    longitude: float
    road_name: str | None = (
        None  # reverse-geocoded; None if lookup failed or road unknown
    )


class CrashStatusEvent(BaseModel):
    incident_id: UUID
    camera_supi: str
    status: CrashNotificationStatus
    channel: CrashNotificationChannel | None = None  # None for DETECTED
    recipient: Annotated[str | None, Field(pattern=r"^[0-9]{15,16}$")] = (
        None  # pedestrian supi for SMS; None otherwise
    )
    location: CrashLocation | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
