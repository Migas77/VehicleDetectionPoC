from enum import Enum
from typing import Any, Annotated, Optional, Self
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.schemas.camara.common import PacketErrorLossRate, Duration

ApplicationProfileId = Annotated[
    UUID, Field(..., description="Identifier for the Application Profile")
]


class ComputeUnitEnum(Enum):
    Kb = "Kb"
    Mb = "Mb"
    Gb = "Gb"
    Tb = "Tb"


TargetMinCPU = Annotated[
    float,
    Field(
        ...,
        description="Number of vCPUs required for the application. Fractional values are allowed (e.g., 0.5 = half a vCPU). The value represents the minimum amount of CPU resources to be allocated to the application instance.",
        examples=[0.5],
    ),
]

TargetMinGPU = Annotated[
    Any,
    Field(
        ...,
        description="This is the target minimun GPUs required by the application\n",
        examples=[1],
    ),
]


class GpuVendorType(Enum):
    Nvidia = "Nvidia"
    AMD = "AMD"


GpuModelName = Annotated[
    str,
    Field(
        ...,
        description="Model name corresponding to vendorType may include info e.g. for NVIDIA, model name could be “Tesla M60”, “Tesla V100” etc.",
    ),
]


class Compute(BaseModel):
    value: Annotated[Optional[int], Field(ge=0, le=1024, examples=[10])] = None
    unit: ComputeUnitEnum | None = None


PacketDelayBudget = Annotated[
    Duration,
    Field(
        description="The packet delay budget is the maximum allowable one-way latency between the customer's device and the gateway from the operator's network to other networks. By limiting the delay, the network can provide an acceptable level of performance for various services, such as voice calls, video streaming, and data. The end-to-end or round trip latency will be about two times this value plus the latency not controlled by the operator"
    ),
]

Jitter = Annotated[
    Duration,
    Field(
        description="The jitter requirement aims to limit the maximum variation in round-trip packet delay for the 99th percentile of traffic, following ITU Y.1540 standards. It considers only acknowledged packets in a session, which are packets that receive a confirmation of receipt from the recipient (e.g., using TCP). This requirement helps maintain consistent latency, essential for real-time applications such as VoIP, video calls, and gaming."
    ),
]


class RateUnitEnum(Enum):
    Bps = "Bps"  # bits per second
    Kbps = "Kbps"
    Mbps = "Mbps"
    Gbps = "Gbps"
    Tbps = "Tbps"


class Rate(BaseModel):
    value: Annotated[
        Optional[int],
        Field(ge=0, le=1024, description="Quantity of rate", examples=[10]),
    ] = None
    unit: Optional[RateUnitEnum] = None


TargetMinDownstreamRate = Annotated[
    Rate, Field(description="This is the target minimum downstream rate.")
]

TargetMinUpstreamRate = Annotated[
    Rate, Field(description="This is the target minimum upstream rate.")
]

TargetMinMemory = Annotated[
    Compute,
    Field(description="This is the target minimum memory required by the application"),
]

TargetMinEphemeralStorage = Annotated[
    Compute,
    Field(
        description="This is the target minimum ephemeral storage required by the application"
    ),
]

TargetMinPersistentStorage = Annotated[
    Compute,
    Field(
        description="This is the target minimum persistent storage required by the application"
    ),
]


class NetworkQualityThresholds(BaseModel):
    packetDelayBudget: PacketDelayBudget | None = None
    targetMinDownstreamRate: TargetMinDownstreamRate | None = None
    targetMinUpstreamRate: TargetMinUpstreamRate | None = None
    packetLossErrorRate: PacketErrorLossRate | None = None
    jitter: Jitter | None = None


class ComputeResourcesThresholds(BaseModel):
    targetMinCPU: TargetMinCPU | None = None
    targetMinMemory: TargetMinMemory | None = None
    gpuVendorType: GpuVendorType | None = None
    gpuModelName: GpuModelName | None = None
    targetMinGPU: TargetMinGPU | None = None
    targetMinGPUMemory: TargetMinMemory | None = None
    targetMinEphemeralStorage: TargetMinEphemeralStorage | None = None
    targetMinPersistentStorage: TargetMinPersistentStorage | None = None


class ApplicationProfile(BaseModel):
    applicationProfileId: ApplicationProfileId
    networkQualityThresholds: NetworkQualityThresholds | None = None
    computeResources: ComputeResourcesThresholds | None = None

    @model_validator(mode="after")
    def at_least_one(self) -> Self:
        if self.networkQualityThresholds is None and self.computeResources is None:
            raise ValueError(
                "At least one of networkQualityThresholds or computeResources must be provided"
            )
        return self


class ApplicationProfileRequest(BaseModel):
    networkQualityThresholds: NetworkQualityThresholds | None = None
    computeResources: ComputeResourcesThresholds | None = None

    @model_validator(mode="after")
    def at_least_one(self) -> Self:
        if self.networkQualityThresholds is None and self.computeResources is None:
            raise ValueError(
                "At least one of networkQualityThresholds or computeResources must be provided"
            )
        return self
