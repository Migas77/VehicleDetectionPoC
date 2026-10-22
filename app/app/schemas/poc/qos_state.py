from enum import Enum

from pydantic import BaseModel


class QosStatus(str, Enum):
    """Outcome reported by a QoS notification (NEF UserPlaneEvent / CAMARA status-changed)."""

    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class CameraQosState(BaseModel):
    """Runtime QoS state of a camera UE, as confirmed by the network's notifications."""

    provisioning_id: str | None  # None while the provisioning creation is in flight
    qos_profile_name: str | None  # applied profile, confirmed by a notification
    pending_qos_profile_name: str | None  # requested profile, awaiting confirmation
