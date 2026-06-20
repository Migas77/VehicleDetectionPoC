from typing import Annotated, Optional

from pydantic import BaseModel, Field


class NefQosCharacteristics(BaseModel):
    """Mirrors the QoSProfile returned by GET /api/v1/qosInfo/qosCharacteristics/{name}."""

    uplinkBitRate: Annotated[
        Optional[int], Field(description="Uplink bandwidth in bps")
    ] = None
    downlinkBitRate: Annotated[
        Optional[int], Field(description="Downlink bandwidth in bps")
    ] = None
    packetDelayBudget: Annotated[
        Optional[int], Field(description="Packet delay budget in ms")
    ] = None
    packerErrRate: Annotated[
        Optional[str], Field(description="Packet error rate (e.g. 4E-2")
    ] = None  # NEF typo preserved


class NefNamedQosCharacteristics(NefQosCharacteristics):
    """Mirrors the NamedQoSProfile returned by GET /api/v1/qosInfo/qosCharacteristics."""

    name: str
