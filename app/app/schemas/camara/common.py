from enum import Enum
from typing import Annotated, Optional, List
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

XCorrelator = Annotated[
    str,
    Field(
        pattern=r"^[a-zA-Z0-9-_:;.\/<>{}]{0,256}$",
        description="Correlation id for the different services",
        examples=["b4333c46-49c0-4f62-80d7-f0ef930f1c46"],
    ),
]

PhoneNumber = Annotated[
    str,
    Field(
        pattern=r"^\+[1-9][0-9]{4,14}$",
        description="A public identifier addressing a telephone subscription. In mobile networks it corresponds to the MSISDN (Mobile Station International Subscriber Directory Number). In order to be globally unique it has to be formatted in international format, according to E.164 standard, prefixed with '+'.",
        examples=["+346661113334"],
    ),
]

NetworkAccessIdentifier = Annotated[
    str,
    Field(
        description="A public identifier addressing a subscription in a mobile network. In 3GPP terminology, it corresponds to the GPSI formatted with the External Identifier ({Local Identifier}@{Domain Identifier}). Unlike the telephone number, the network access identifier is not subjected to portability ruling in force, and is individually managed by each operator.",
        examples=["123456789@domain.com"],
    ),
]

Port = Annotated[int, Field(ge=0, le=65535, description="TCP or UDP port number")]

Latitude = Annotated[
    float,
    Field(
        ge=-90.0,
        le=90.0,
        description="Latitude component of a location.",
        examples=[50.735851],
    ),
]

Longitude = Annotated[
    float,
    Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude component of location.",
        examples=[7.10066],
    ),
]


class Point(BaseModel):
    latitude: Latitude
    longitude: Longitude


LastStatusTime = Annotated[
    datetime,
    Field(
        description="Last time that the associated device reachability status was updated",
        examples=["2024-02-20T10:41:38.657Z"],
    ),
]

ApplicationServerIpv4Address = Annotated[
    str,
    Field(
        description="IPv4 address may be specified in form <address/mask> as:\n  - address - an IPv4 number in dotted-quad form 1.2.3.4. Only this exact IP number will match the flow control rule.\n  - address/mask - an IP number as above with a mask width of the form 1.2.3.4/24.\n    In this case, all IP numbers from 1.2.3.0 to 1.2.3.255 will match. The bit width MUST be valid for the IP version.",
        examples=["192.168.0.1/24"],
    ),
]

ApplicationServerIpv6Address = Annotated[
    str,
    Field(
        description="IPv6 address may be specified in form <address/mask> as:\n  - address - The /128 subnet is optional for single addresses:\n    - 2001:db8:85a3:8d3:1319:8a2e:370:7344\n    - 2001:db8:85a3:8d3:1319:8a2e:370:7344/128\n  - address/mask - an IP v6 number with a mask:\n    - 2001:db8:85a3:8d3::0/64\n    - 2001:db8:85a3:8d3::/64",
        examples=["2001:db8:85a3:8d3:1319:8a2e:370:7344"],
    ),
]


class ApplicationServer(BaseModel):
    ipv4Address: Optional[ApplicationServerIpv4Address] = None
    ipv6Address: Optional[ApplicationServerIpv6Address] = None


class Range(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)
    from_: Annotated[Port, Field(alias="from")]
    to: Port


class PortsSpec(BaseModel):
    ranges: Annotated[
        Optional[List[Range]],
        Field(description="Range of TCP or UDP ports", min_length=1),
    ] = None
    ports: Annotated[
        Optional[List[Port]],
        Field(description="Array of TCP or UDP ports", min_length=1),
    ] = None


class TimeUnitEnum(Enum):
    Days = "Days"
    Hours = "Hours"
    Minutes = "Minutes"
    Seconds = "Seconds"
    Milliseconds = "Milliseconds"
    Microseconds = "Microseconds"
    Nanoseconds = "Nanoseconds"


class Duration(BaseModel):
    value: Annotated[
        Optional[int], Field(ge=1, description="Quantity of duration", examples=[12])
    ] = None
    unit: Optional[TimeUnitEnum] = None


PacketErrorLossRate = Annotated[
    int,
    Field(
        ...,
        ge=1,
        le=10,
        description="The exponential power of the allowable error loss rate 10^(-N). For instance 3 would be an error loss rate of 10 to the power of -3 (0.001)\nFor 5G network the 3GPP specification TS 23.203 defines the packet error loss rate QCI attribute. It describes the Quality of Service (QoS) Class Identifier (QCI) parameters used to differentiate traffic classes in mobile networks, ensuring appropriate resource allocation and performance for various services.\nThe packet error loss rate is one of the QCI attributes, providing information on the acceptable packet loss rate for a specific traffic class. This attribute helps maintain the desired performance level for services like voice calls, video streaming, or data transfers within the 3GPP mobile network.",
        examples=[3],
    ),
]
