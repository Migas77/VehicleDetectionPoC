from app.schemas.camara.application_profiles import Rate, RateUnitEnum
from app.schemas.camara.connectivity_insights_subscriptions import (
    NetworkQualityThresholdsConfidence,
)

_BITRATE_MULTIPLIERS: dict[str, int] = {
    "Bps": 1,  # same as bps (I think CAMARA just capitalized it without meaning to)
    "bps": 1,
    "Kbps": 1_000,
    "kbps": 1_000,  # same as Kbps (I think CAMARA just capitalized it without meaning to)
    "Mbps": 1_000_000,
    "Gbps": 1_000_000_000,
    "Tbps": 1_000_000_000_000,
}


def bitrate_str_to_bps(bitrate: str) -> int:
    """Convert a BitRate string (e.g. '10 Mbps') to an integer number of bps."""
    value_str, unit = bitrate.split(" ")
    return int(float(value_str) * _BITRATE_MULTIPLIERS[unit])


def rate_to_bps(value: int, unit: str) -> int:
    return int(value * _BITRATE_MULTIPLIERS[unit])


_UNIT_TO_RATE_ENUM: dict[str, RateUnitEnum] = {
    "bps": RateUnitEnum.Bps,
    "Bps": RateUnitEnum.Bps,
    "Kbps": RateUnitEnum.Kbps,
    "kbps": RateUnitEnum.Kbps,
    "Mbps": RateUnitEnum.Mbps,
    "Gbps": RateUnitEnum.Gbps,
    "Tbps": RateUnitEnum.Tbps,
}


def bitrate_str_to_rate(bitrate: str) -> Rate:
    """Convert a BitRate string (e.g. '100 Kbps') to a CAMARA Rate object."""
    value_str, unit = bitrate.split(" ")
    return Rate(value=int(float(value_str)), unit=_UNIT_TO_RATE_ENUM[unit])


def compare_min_rate_to_nef_bitrate(
    min_threshold: Rate, nef_bitrate: str
) -> NetworkQualityThresholdsConfidence:
    """Return whether the NEF bitrate meets the CAMARA Rate threshold."""
    if min_threshold.value is None or min_threshold.unit is None:
        return NetworkQualityThresholdsConfidence.meets_the_application_requirements
    nef_bps = bitrate_str_to_bps(nef_bitrate)
    min_threshold_bps = rate_to_bps(min_threshold.value, min_threshold.unit.value)
    if nef_bps >= min_threshold_bps:
        return NetworkQualityThresholdsConfidence.meets_the_application_requirements
    return (
        NetworkQualityThresholdsConfidence.unable_to_meet_the_application_requirements
    )
