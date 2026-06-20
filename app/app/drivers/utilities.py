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
