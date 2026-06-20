from pydantic import BaseModel

from app.drivers.utilities import bitrate_str_to_bps
from app.schemas.nef.analytics_exposure import BitRate


class QosProfile(BaseModel):
    qos_profile_name: str
    ul_bitrate: BitRate
    dl_bitrate: BitRate

    def ul_bitrate_bps(self) -> int:
        return bitrate_str_to_bps(self.ul_bitrate)

    def dl_bitrate_bps(self) -> int:
        return bitrate_str_to_bps(self.dl_bitrate)
