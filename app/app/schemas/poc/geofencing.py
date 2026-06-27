from enum import Enum

from pydantic import BaseModel

from app.schemas.camara.geofencing import SubscriptionEventType
from app.schemas.poc.area import SurveyedArea


class GeofenceState(str, Enum):
    INSIDE = "INSIDE"
    OUTSIDE = "OUTSIDE"


class ManagedGeofencingSubscription(BaseModel):
    """A geofencing subscription managed entirely by the app for the NEF backend.

    NEF exposes no geofencing primitive, only LOCATION_REPORTING monitoring, so the
    enter/leave logic is computed in the callback and the whole object is stored in Redis.
    """

    subscription_id: str
    ue_supi: str
    area: SurveyedArea
    types: list[SubscriptionEventType]  # [v0_area_entered, v0_area_left]
    nef_subscription_url: str  # NEF monitoring 'self' link, for deletion
    last_state: GeofenceState | None = None
