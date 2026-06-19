from pydantic import BaseModel

from app.schemas.nef.analytics_exposure import BitRate


class QosProfile(BaseModel):
    qos_profile_id: str | None = None  # set after QoS profile creation via API
    qos_profile_name: str
    ul_bitrate: BitRate
    dl_bitrate: BitRate
