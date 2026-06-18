from enum import Enum
from typing import Annotated, Optional, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter

from app.schemas.camara import subscriptions
from app.schemas.camara.application_profiles import ApplicationProfileId
from app.schemas.camara.common import ApplicationServer, PortsSpec
from app.schemas.camara.device import Device
from app.schemas.camara.subscriptions import (
    SubscriptionId,
    BaseSubscription,
    Protocol,
    HTTPSettings,
    MQTTSettings,
    AMQPSettings,
    ApacheKafkaSettings,
    NATSSettings,
    SinkCredential,
)

AliasedSubscriptionId = Annotated[
    SubscriptionId,
    Field(
        serialization_alias="subscriptionId",
    ),
]


class SignalStrength(Enum):
    excellent = "excellent"
    good = "good"
    fair = "fair"
    poor = "poor"
    no_signal = "no signal"


class ConnectivityType(Enum):
    field_5G_SA = "5G-SA"
    field_5G_NSA = "5G-NSA"
    field_4G = "4G"
    field_3G = "3G"


class AdditionalKpis(BaseModel):
    signalStrength: SignalStrength | None = Field(
        None,
        description="rough indication of the end user device radio signal conditions\n",
    )
    connectivityType: ConnectivityType | None = Field(
        None,
        description="the access technology connecting the user device to the operator\nnetwork\n",
    )


class NetworkQualityThresholdsConfidence(Enum):
    meets_the_application_requirements = "meets the application requirements"
    unable_to_meet_the_application_requirements = (
        "unable to meet the application requirements"
    )


class TerminationReason(Enum):
    # Doesn't match the one in subscriptions.py (which has 1 additional value: SUBSCRIPTION_UNPROCESSABLE)
    # Therefore, the one is subscriptions.py will be used, and then converted back to this when constructing payload
    MAX_EVENTS_REACHED = "MAX_EVENTS_REACHED"
    NETWORK_TERMINATED = "NETWORK_TERMINATED"
    SUBSCRIPTION_EXPIRED = "SUBSCRIPTION_EXPIRED"
    ACCESS_TOKEN_EXPIRED = "ACCESS_TOKEN_EXPIRED"
    SUBSCRIPTION_DELETED = "SUBSCRIPTION_DELETED"


class EventTypeNotification(str, Enum):
    org_camaraproject_connectivity_insights_subscriptions_v0_network_quality = (
        "org.camaraproject.connectivity-insights-subscriptions.v0.network-quality"
    )
    org_camaraproject_connectivity_insights_subscriptions_v0_subscription_ended = (
        "org.camaraproject.connectivity-insights-subscriptions.v0.subscription-ended"
    )


class SubscriptionEventType(str, Enum):
    org_camaraproject_connectivity_insights_subscriptions_v0_network_quality = (
        "org.camaraproject.connectivity-insights-subscriptions.v0.network-quality"
    )


class NetworkQualityInsight(BaseModel):
    papplicationProfileId: ApplicationProfileId | None = None
    packetDelayBudget: NetworkQualityThresholdsConfidence | None = None
    targetMinDownstreamRate: NetworkQualityThresholdsConfidence | None = None
    targetMinUpstreamRate: NetworkQualityThresholdsConfidence | None = None
    packetlossErrorRate: NetworkQualityThresholdsConfidence | None = None
    jitter: NetworkQualityThresholdsConfidence | None = None
    additionalKpis: AdditionalKpis | None = None


class SubscriptionEnded(BaseModel):
    terminationReason: TerminationReason
    subscriptionId: SubscriptionId
    terminationDescription: str | None = Field(
        None, description="Explanation why a subscription ended or had to end."
    )


class CreateSubscriptionDetail(BaseModel):
    device: Device
    applicationServer: ApplicationServer | None = None
    applicationServerPorts: PortsSpec | None = Field(
        None,
        description="A list of single ports or port ranges on the application server\n",
    )
    applicationProfileId: ApplicationProfileId


CloudEventData = Union[Optional[NetworkQualityInsight], Optional[SubscriptionEnded]]
CloudEvent = subscriptions.CloudEvent[EventTypeNotification, CloudEventData]
Subscription = subscriptions.Subscription[
    SubscriptionEventType, CreateSubscriptionDetail
]
SubscriptionTypeAdapter: TypeAdapter[Subscription] = TypeAdapter(Subscription)
SubscriptionRequest = subscriptions.SubscriptionRequest[
    SubscriptionEventType, CreateSubscriptionDetail
]
SubscriptionRequestTypeAdapter: TypeAdapter[SubscriptionRequest] = TypeAdapter(
    SubscriptionRequest
)


# Connectivity Insights Subscription Response Model (used at the API boundary to match spec API and swagger)
# Subscription with identifier aliased to subscriptionId
# Also removes sinkCredential as it's not passed in this API
# (internal logic uses the same Subscription format as other APIs from subscriptions.py)


class ConnectivityInsightsSubscriptionsBase[
    SubscriptionEventType: str,
    SubscriptionDetails,
](BaseSubscription[SubscriptionEventType, SubscriptionDetails]):
    id: AliasedSubscriptionId
    sinkCredential: Optional[SinkCredential] = Field(exclude=True)


class HTTPSubscriptionResponse[SubscriptionEventType: str, SubscriptionDetail](
    ConnectivityInsightsSubscriptionsBase[SubscriptionEventType, SubscriptionDetail]
):
    protocol: Literal[Protocol.HTTP]
    protocolSettings: Optional[HTTPSettings] = None


class MQTTSubscriptionResponse[SubscriptionEventType: str, SubscriptionDetail](
    ConnectivityInsightsSubscriptionsBase[SubscriptionEventType, SubscriptionDetail]
):
    protocol: Union[Literal[Protocol.MQTT3], Literal[Protocol.MQTT5]]
    protocolSettings: Optional[MQTTSettings] = None


class AMQPSubscriptionResponse[SubscriptionEventType: str, SubscriptionDetail](
    ConnectivityInsightsSubscriptionsBase[SubscriptionEventType, SubscriptionDetail]
):
    protocol: Literal[Protocol.AMQP]
    protocolSettings: Optional[AMQPSettings] = None


class ApacheKafkaSubscriptionResponse[SubscriptionEventType: str, SubscriptionDetail](
    ConnectivityInsightsSubscriptionsBase[SubscriptionEventType, SubscriptionDetail]
):
    protocol: Literal[Protocol.KAFKA]
    protocolSettings: Optional[ApacheKafkaSettings] = None


class NATSSubscriptionResponse[SubscriptionEventType: str, SubscriptionDetail](
    ConnectivityInsightsSubscriptionsBase[SubscriptionEventType, SubscriptionDetail]
):
    protocol: Literal[Protocol.NATS]
    protocolSettings: Optional[NATSSettings] = None


type ConnectivityInsightsSubscription[
    SubscriptionEventType: str,
    SubscriptionDetail,
] = Annotated[
    Union[
        HTTPSubscriptionResponse[SubscriptionEventType, SubscriptionDetail],
        MQTTSubscriptionResponse[SubscriptionEventType, SubscriptionDetail],
        AMQPSubscriptionResponse[SubscriptionEventType, SubscriptionDetail],
        ApacheKafkaSubscriptionResponse[SubscriptionEventType, SubscriptionDetail],
        NATSSubscriptionResponse[SubscriptionEventType, SubscriptionDetail],
    ],
    Field(discriminator="protocol"),
]

CISSubscription = ConnectivityInsightsSubscription[
    SubscriptionEventType, CreateSubscriptionDetail
]
CISSubscriptionTypeAdapter: TypeAdapter[CISSubscription] = TypeAdapter(CISSubscription)


# TODO: verify sinkCredential for the rest of stuff (on BaseSubscription)
