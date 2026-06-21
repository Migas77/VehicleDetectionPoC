from pydantic import BaseModel

from app.drivers.utilities import bitrate_str_to_bps
from app.schemas.nef.analytics_exposure import BitRate


class QosProfile(BaseModel):
    qos_profile_name: str
    min_ul_bitrate: BitRate
    max_ul_bitrate: BitRate
    min_dl_bitrate: BitRate
    max_dl_bitrate: BitRate

    def min_ul_bitrate_bps(self) -> int:
        return bitrate_str_to_bps(self.min_ul_bitrate)

    def max_ul_bitrate_bps(self) -> int:
        return bitrate_str_to_bps(self.max_ul_bitrate)

    def min_dl_bitrate_bps(self) -> int:
        return bitrate_str_to_bps(self.min_dl_bitrate)

    def max_dl_bitrate_bps(self) -> int:
        return bitrate_str_to_bps(self.max_dl_bitrate)
