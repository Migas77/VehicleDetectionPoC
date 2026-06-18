from enum import Enum
from typing import Annotated, Union, Optional
from uuid import UUID

from pydantic import AwareDatetime, Base64Str, BaseModel, Field, RootModel

from app.schemas.nef.commonData import SupportedFeatures


class AnalyticsEvent(Enum):
    """Represents the analytics event that is subscribed or notified.  \nPossible values are:\n- UE_MOBILITY: The AF requests to be notified about analytics information of UE mobility.\n- UE_COMM: The AF requests to be notified about analytics information of UE communication.\n- ABNORMAL_BEHAVIOR: The AF requests to be notified about analytics information of UE's\n  abnormal behavior.\n- CONGESTION: The AF requests to be notified about analytics information of user data\n  congestion information. \n- NETWORK_PERFORMANCE: The AF requests to be notified about analytics information\n  of network performance. \n- QOS_SUSTAINABILITY: The AF requests to be notified about analytics information\n  of QoS sustainability.\n- DISPERSION: The AF requests to be notified about analytics information of Dispersion\n  analytics.\n- DN_PERFORMANCE: The AF requests to be notified about analytics information of DN\n  performance.\n- SERVICE_EXPERIENCE: The AF requests to be notified about analytics information of service\n  experience.\n- E2E_DATA_VOL_TRANS_TIME: The AF requests to be notified about analytics information of\n  E2E data volume transfer time.\n- MOVEMENT_BEHAVIOUR: The AF requests to be notified about analytics information of\n  Movement Behaviour.\n- RELATIVE_PROXIMITY: The AF requests to be notified about analytics information of\n  Relative Proximity.\n- WLAN_PERFORMANCE: Indicates that the event subscribed is the Wlan Performance\n  information.\n- NS_LOAD_LEVEL: Indicates that the event subscribed is load level information of Network\n  Slice.\n"""

    UE_MOBILITY = "UE_MOBILITY"
    UE_COMM = "UE_COMM"
    ABNORMAL_BEHAVIOR = "ABNORMAL_BEHAVIOR"
    CONGESTION = "CONGESTION"
    NETWORK_PERFORMANCE = "NETWORK_PERFORMANCE"
    QOS_SUSTAINABILITY = "QOS_SUSTAINABILITY"
    DISPERSION = "DISPERSION"
    DN_PERFORMANCE = "DN_PERFORMANCE"
    SERVICE_EXPERIENCE = "SERVICE_EXPERIENCE"
    E2E_DATA_VOL_TRANS_TIME = "E2E_DATA_VOL_TRANS_TIME"
    MOVEMENT_BEHAVIOUR = "MOVEMENT_BEHAVIOUR"
    RELATIVE_PROXIMITY = "RELATIVE_PROXIMITY"
    WLAN_PERFORMANCE = "WLAN_PERFORMANCE"
    NS_LOAD_LEVEL = "NS_LOAD_LEVEL"


class AnalyticsFailureCode(Enum):
    """Identifies the failure reason.  \nPossible values are:\n- UNAVAILABLE_DATA: The event is rejected since necessary data to perform the service\n  is unavailable.\n- BOTH_STAT_PRED_NOT_ALLOWED: The event is rejected since the start time is in the past\n  and the end time is in the future, which means the NF service consumer requested both\n  statistics and prediction for the analytics.\n- UNSATISFIED_REQUESTED_ANALYTICS_TIME: Indicates that the requested event is rejected\n  since the analytics information is not ready when the time indicated by the timeAnaNeeded\n  attribute (as provided during the creation or modification of subscription) is reached.\n- NO_ROAMING_SUPPORT: Indicates that the request shall be rejected because roaming analytics\n  or data are required and the NWDAF that was invoked by the NEF neither supported roaming\n  exchange capabilitiy nor could it forward the request to another NWDAF.\n- OTHER: The event is rejected due to other reasons.\n"""

    UNAVAILABLE_DATA = "UNAVAILABLE_DATA"
    BOTH_STAT_PRED_NOT_ALLOWED = "BOTH_STAT_PRED_NOT_ALLOWED"
    UNSATISFIED_REQUESTED_ANALYTICS_TIME = "UNSATISFIED_REQUESTED_ANALYTICS_TIME"
    NO_ROAMING_SUPPORT = "NO_ROAMING_SUPPORT"
    OTHER = "OTHER"


class NetworkPerfType(Enum):
    """Represents the network performance types.  \nPossible values are:\n- GNB_ACTIVE_RATIO: Indicates that the network performance requirement is gNodeB active\n  (i.e. up and running) rate. Indicates the ratio of gNB active (i.e. up and running) number\n  to the total number of gNB.\n- GNB_COMPUTING_USAGE: Indicates gNodeB computing resource usage.\n- GNB_MEMORY_USAGE: Indicates gNodeB memory usage.\n- GNB_DISK_USAGE: Indicates gNodeB disk usage.\n- GNB_RSC_USAGE_OVERALL_TRAFFIC: The gNB resource usage.\n- GNB_RSC_USAGE_GBR_TRAFFIC: The gNB resource usage for GBR traffic.\n- GNB_RSC_USAGE_DELAY_CRIT_GBR_TRAFFIC: The gNB resource usage for Delay-critical GBR\n  traffic.\n- NUM_OF_UE: Indicates number of UEs.\n- SESS_SUCC_RATIO: Indicates ratio of successful setup of PDU sessions to total PDU\n  session setup attempts.\n- HO_SUCC_RATIO: Indicates Ratio of successful handovers to the total handover attempts.\n"""

    GNB_ACTIVE_RATIO = "GNB_ACTIVE_RATIO"
    GNB_COMPUTING_USAGE = "GNB_COMPUTING_USAGE"
    GNB_MEMORY_USAGE = "GNB_MEMORY_USAGE"
    GNB_DISK_USAGE = "GNB_DISK_USAGE"
    GNB_RSC_USAGE_OVERALL_TRAFFIC = "GNB_RSC_USAGE_OVERALL_TRAFFIC"
    GNB_RSC_USAGE_GBR_TRAFFIC = "GNB_RSC_USAGE_GBR_TRAFFIC"
    GNB_RSC_USAGE_DELAY_CRIT_GBR_TRAFFIC = "GNB_RSC_USAGE_DELAY_CRIT_GBR_TRAFFIC"
    NUM_OF_UE = "NUM_OF_UE"
    SESS_SUCC_RATIO = "SESS_SUCC_RATIO"
    HO_SUCC_RATIO = "HO_SUCC_RATIO"


SamplingRatio = Annotated[
    int,
    Field(
        ...,
        ge=1,
        le=100,
        description="Unsigned integer indicating Sampling Ratio (see clauses 4.15.1 of 3GPP TS 23.502), expressed in percent. \n",
    ),
]

Uinteger = Annotated[
    int,
    Field(
        ...,
        ge=0,
        description="Unsigned Integer, i.e. only value 0 and integers above 0 are permissible.",
    ),
]


class NetworkPerfOrderCriterion(Enum):
    """Represents the ordering criterion for the list of network performance analytics.  \nPossible values are:  \n  - NUMBER_OF_UES: The ordering criterion of the analytics is the number of UEs.\n  - COMMUNICATION_PERF: The ordering criterion of the analytics is the communication performance.\n  - MOBILITY_PERF: The ordering criterion of the analytics is themobility performance.\n"""

    NUMBER_OF_UES = "NUMBER_OF_UES"
    COMMUNICATION_PERF = "COMMUNICATION_PERF"
    MOBILITY_PERF = "MOBILITY_PERF"


class TrafficDirection(Enum):
    """Represents the traffic direction for the resource usage information.  \nPossible values are:  \n  - UL_AND_DL: Uplink and downlink traffic.\n  - UL: Uplink traffic.\n  - DL: Downlink traffic.\n"""

    UL_AND_DL = "UL_AND_DL"
    UL = "UL"
    DL = "DL"


class ValueExpression(Enum):
    """Represents the average or peak value of the resource usage for the network performance type.  \nPossible values are:  \n  - AVERAGE: Resource usage information in average value.\n  - PEAK: Resource usage information in peak value.\n"""

    AVERAGE = "AVERAGE"
    PEAK = "PEAK"


class ResourceUsageRequirement(BaseModel):
    tfcDirc: TrafficDirection | None = None
    valExp: ValueExpression | None = None


class NetworkPerfRequirement(BaseModel):
    nwPerfType: NetworkPerfType
    relativeRatio: SamplingRatio | None = None
    absoluteNum: Uinteger | None = None
    orderCriterion: NetworkPerfOrderCriterion | None = None
    rscUsgReq: ResourceUsageRequirement | None = None


class GeographicalCoordinates(BaseModel):
    lon: Annotated[float, Field(ge=-180.0, le=180.0)]
    lat: Annotated[float, Field(ge=-90.0, le=90.0)]


Uncertainty = Annotated[
    float, Field(..., ge=0.0, description="Indicates value of uncertainty.")
]

Orientation = Annotated[
    int, Field(..., ge=0, le=180, description="Indicates value of orientation angle.")
]


class UncertaintyEllipse(BaseModel):
    semiMajor: Uncertainty
    semiMinor: Uncertainty
    orientationMajor: Orientation


Confidence = Annotated[
    int, Field(..., ge=0, le=100, description="Indicates value of confidence.")
]

PointList = Annotated[
    list[GeographicalCoordinates],
    Field(..., description="List of points.", max_length=15, min_length=3),
]

Altitude = Annotated[
    float,
    Field(..., ge=-32767.0, le=32767.0, description="Indicates value of altitude."),
]

InnerRadius = Annotated[
    int, Field(..., ge=0, le=327675, description="Indicates value of the inner radius.")
]

Angle = Annotated[
    int, Field(..., ge=0, le=360, description="Indicates value of angle.")
]

HorizAxesOrientation = Annotated[
    int,
    Field(
        ...,
        ge=0,
        le=3600,
        description="Horizontal axes orientation angle clockwise from northing in 0.1 degrees.",
    ),
]


class RelativeCartesianLocation(BaseModel):
    x: float
    y: float
    z: float | None = None


class UncertaintyEllipsoid(BaseModel):
    semiMajor: Uncertainty
    semiMinor: Uncertainty
    vertical: Uncertainty
    orientationMajor: Orientation


class SupportedGADShapes(Enum):
    """Indicates supported GAD shapes."""

    POINT = "POINT"
    POINT_UNCERTAINTY_CIRCLE = "POINT_UNCERTAINTY_CIRCLE"
    POINT_UNCERTAINTY_ELLIPSE = "POINT_UNCERTAINTY_ELLIPSE"
    POLYGON = "POLYGON"
    POINT_ALTITUDE = "POINT_ALTITUDE"
    POINT_ALTITUDE_UNCERTAINTY = "POINT_ALTITUDE_UNCERTAINTY"
    ELLIPSOID_ARC = "ELLIPSOID_ARC"
    LOCAL_2D_POINT_UNCERTAINTY_ELLIPSE = "LOCAL_2D_POINT_UNCERTAINTY_ELLIPSE"
    LOCAL_3D_POINT_UNCERTAINTY_ELLIPSOID = "LOCAL_3D_POINT_UNCERTAINTY_ELLIPSOID"
    DISTANCE_DIRECTION = "DISTANCE_DIRECTION"
    RELATIVE_2D_LOCATION_UNCERTAINTY_ELLIPSE = (
        "RELATIVE_2D_LOCATION_UNCERTAINTY_ELLIPSE"
    )
    RELATIVE_3D_LOCATION_UNCERTAINTY_ELLIPSOID = (
        "RELATIVE_3D_LOCATION_UNCERTAINTY_ELLIPSOID"
    )


class CivicAddress(BaseModel):
    country: str | None = None
    A1: str | None = None
    A2: str | None = None
    A3: str | None = None
    A4: str | None = None
    A5: str | None = None
    A6: str | None = None
    PRD: str | None = None
    POD: str | None = None
    STS: str | None = None
    HNO: str | None = None
    HNS: str | None = None
    LMK: str | None = None
    LOC: str | None = None
    NAM: str | None = None
    PC: str | None = None
    BLD: str | None = None
    UNIT: str | None = None
    FLR: str | None = None
    ROOM: str | None = None
    PLC: str | None = None
    PCN: str | None = None
    POBOX: str | None = None
    ADDCODE: str | None = None
    SEAT: str | None = None
    RD: str | None = None
    RDSEC: str | None = None
    RDBR: str | None = None
    RDSUBBR: str | None = None
    PRM: str | None = None
    POM: str | None = None
    usageRules: str | None = None
    method: str | None = None
    providedBy: str | None = None


Mcc = Annotated[
    str,
    Field(
        ...,
        pattern=r"^\d{3}$",
        description="Mobile Country Code part of the PLMN, comprising 3 digits, as defined in clause 9.3.3.5 of 3GPP TS 38.413. \n",
    ),
]


Mnc = Annotated[
    str,
    Field(
        ...,
        pattern=r"^\d{2,3}$",
        description="Mobile Network Code part of the PLMN, comprising 2 or 3 digits, as defined in  clause 9.3.3.5 of 3GPP TS 38.413. \n",
    ),
]


class PlmnId(BaseModel):
    mcc: Mcc
    mnc: Mnc


EutraCellId = Annotated[
    str,
    Field(
        ...,
        pattern=r"^[A-Fa-f0-9]{7}$",
        description='28-bit string identifying an E-UTRA Cell Id as specified in clause 9.3.1.9 of  3GPP TS 38.413, in hexadecimal representation. Each character in the string shall take a  value of "0" to "9", "a" to "f" or "A" to "F" and shall represent 4 bits. The most  significant character representing the 4 most significant bits of the Cell Id shall appear  first in the string, and the character representing the 4 least significant bit of the  Cell Id shall appear last in the string. \n',
    ),
]


Nid = Annotated[
    str,
    Field(
        ...,
        pattern=r"^[A-Fa-f0-9]{11}$",
        description="This represents the Network Identifier, which together with a PLMN ID is used to identify an SNPN (see 3GPP TS 23.003 and 3GPP TS 23.501 clause 5.30.2.1). \n",
    ),
]


class Ecgi(BaseModel):
    plmnId: PlmnId
    eutraCellId: EutraCellId
    nid: Nid | None = None


NrCellId = Annotated[
    str,
    Field(
        ...,
        pattern=r"^[A-Fa-f0-9]{9}$",
        description='36-bit string identifying an NR Cell Id as specified in clause 9.3.1.7 of 3GPP TS 38.413,  in hexadecimal representation. Each character in the string shall take a value of "0" to "9",  "a" to "f" or "A" to "F" and shall represent 4 bits. The most significant character  representing the 4 most significant bits of the Cell Id shall appear first in the string, and  the character representing the 4 least significant bit of the Cell Id shall appear last in the  string. \n',
    ),
]


class Ncgi(BaseModel):
    plmnId: PlmnId
    nrCellId: NrCellId
    nid: Nid | None = None


N3IwfId = Annotated[
    str,
    Field(
        ...,
        pattern=r"^[A-Fa-f0-9]+$",
        description='This represents the identifier of the N3IWF ID as specified in clause 9.3.1.57 of  3GPP TS 38.413 in hexadecimal representation. Each character in the string shall take a value  of "0" to "9", "a" to "f" or "A" to "F" and shall represent 4 bits. The most significant  character representing the 4 most significant bits of the N3IWF ID shall appear first in the  string, and the character representing the 4 least significant bit of the N3IWF ID shall  appear last in the string. \n',
    ),
]


class GNbId(BaseModel):
    bitLength: Annotated[
        int,
        Field(
            ...,
            ge=22,
            le=32,
            description="Unsigned integer representing the bit length of the gNB ID as defined in clause 9.3.1.6 of 3GPP TS 38.413 [11], within the range 22 to 32.\n",
        ),
    ]
    gNBValue: Annotated[
        str,
        Field(
            ...,
            pattern=r"^[A-Fa-f0-9]{6,8}$",
            description='This represents the identifier of the gNB. The value of the gNB ID shall be encoded in hexadecimal representation. Each character in the string shall take a value of "0" to "9", "a" to "f" or "A" to "F" and shall represent 4 bits. The padding 0 shall be added to make multiple nibbles,  the most significant character representing the padding 0 if required together with the 4 most significant bits of the gNB ID shall appear first in the string, and the character representing the 4 least significant bit of the gNB ID shall appear last in the string.\n',
        ),
    ]


NgeNbId = Annotated[
    str,
    Field(
        ...,
        pattern=r"^(MacroNGeNB-[A-Fa-f0-9]{5}|LMacroNGeNB-[A-Fa-f0-9]{6}|SMacroNGeNB-[A-Fa-f0-9]{5})$",
        description='This represents the identifier of the ng-eNB ID as specified in clause 9.3.1.8 of  3GPP TS 38.413. The value of the ng-eNB ID shall be encoded in hexadecimal representation.  Each character in the string shall take a value of "0" to "9", "a" to "f" or "A" to "F" and  shall represent 4 bits. The padding 0 shall be added to make multiple nibbles, so the most  significant character representing the padding 0 if required together with the 4 most  significant bits of the ng-eNB ID shall appear first in the string, and the character  representing the 4 least significant bit of the ng-eNB ID (to form a nibble) shall appear last  in the string. \n',
        examples=["SMacroNGeNB-34B89"],
    ),
]


WAgfId = Annotated[
    str,
    Field(
        ...,
        pattern=r"^[A-Fa-f0-9]+$",
        description='This represents the identifier of the W-AGF ID as specified in clause 9.3.1.162 of  3GPP TS 38.413 in hexadecimal representation. Each character in the string shall take a value  of "0" to "9", "a" to "f" or "A" to "F" and shall represent 4 bits. The most significant  character representing the 4 most significant bits of the W-AGF ID shall appear first in the  string, and the character representing the 4 least significant bit of the W-AGF ID shall  appear last in the string. \n',
    ),
]


TngfId = Annotated[
    str,
    Field(
        ...,
        pattern=r"^[A-Fa-f0-9]+$",
        description='This represents the identifier of the TNGF ID as specified in clause 9.3.1.161 of  3GPP TS 38.413  in hexadecimal representation. Each character in the string shall take a value of "0" to "9", "a"  to "f" or "A" to "F" and shall represent 4 bits. The most significant character representing the  4 most significant bits of the TNGF ID shall appear first in the string, and the character  representing the 4 least significant bit of the TNGF ID shall appear last in the string. \n',
    ),
]


ENbId = Annotated[
    str,
    Field(
        ...,
        pattern=r"^(MacroeNB-[A-Fa-f0-9]{5}|LMacroeNB-[A-Fa-f0-9]{6}|SMacroeNB-[A-Fa-f0-9]{5}|HomeeNB-[A-Fa-f0-9]{7})$",
        description='This represents the identifier of the eNB ID as specified in clause 9.2.1.37 of  3GPP TS 36.413. The string shall be formatted with the following pattern  \'^(\'MacroeNB-[A-Fa-f0-9]{5}|LMacroeNB-[A-Fa-f0-9]{6}|SMacroeNB-[A-Fa-f0-9]{5} |HomeeNB-[A-Fa-f0-9]{7})$\'. The value of the eNB ID shall be encoded in hexadecimal representation. Each character in the  string shall take a value of "0" to "9", "a" to "f" or "A" to "F" and shall represent 4 bits.  The padding 0 shall be added to make multiple nibbles, so the most significant character  representing the padding 0 if required together with the 4 most significant bits of the eNB ID  shall appear first in the string, and the character representing the 4 least significant bit  of the eNB ID (to form a nibble) shall appear last in the string.\n',
    ),
]


class GlobalRanNodeId1(BaseModel):
    plmnId: PlmnId
    n3IwfId: N3IwfId
    gNbId: GNbId | None = None
    ngeNbId: NgeNbId | None = None
    wagfId: WAgfId | None = None
    tngfId: TngfId | None = None
    nid: Nid | None = None
    eNbId: ENbId | None = None


class GlobalRanNodeId2(BaseModel):
    plmnId: PlmnId
    n3IwfId: N3IwfId | None = None
    gNbId: GNbId
    ngeNbId: NgeNbId | None = None
    wagfId: WAgfId | None = None
    tngfId: TngfId | None = None
    nid: Nid | None = None
    eNbId: ENbId | None = None


class GlobalRanNodeId3(BaseModel):
    plmnId: PlmnId
    n3IwfId: N3IwfId | None = None
    gNbId: GNbId | None = None
    ngeNbId: NgeNbId
    wagfId: WAgfId | None = None
    tngfId: TngfId | None = None
    nid: Nid | None = None
    eNbId: ENbId | None = None


class GlobalRanNodeId4(BaseModel):
    plmnId: PlmnId
    n3IwfId: N3IwfId | None = None
    gNbId: GNbId | None = None
    ngeNbId: NgeNbId | None = None
    wagfId: WAgfId
    tngfId: TngfId | None = None
    nid: Nid | None = None
    eNbId: ENbId | None = None


class GlobalRanNodeId5(BaseModel):
    plmnId: PlmnId
    n3IwfId: N3IwfId | None = None
    gNbId: GNbId | None = None
    ngeNbId: NgeNbId | None = None
    wagfId: WAgfId | None = None
    tngfId: TngfId
    nid: Nid | None = None
    eNbId: ENbId | None = None


class GlobalRanNodeId6(BaseModel):
    plmnId: PlmnId
    n3IwfId: N3IwfId | None = None
    gNbId: GNbId | None = None
    ngeNbId: NgeNbId | None = None
    wagfId: WAgfId | None = None
    tngfId: TngfId | None = None
    nid: Nid | None = None
    eNbId: ENbId


class GlobalRanNodeId(
    RootModel[
        Union[
            GlobalRanNodeId1,
            GlobalRanNodeId2,
            GlobalRanNodeId3,
            GlobalRanNodeId4,
            GlobalRanNodeId5,
            GlobalRanNodeId6,
        ]
    ]
):
    root: Annotated[
        Union[
            GlobalRanNodeId1,
            GlobalRanNodeId2,
            GlobalRanNodeId3,
            GlobalRanNodeId4,
            GlobalRanNodeId5,
            GlobalRanNodeId6,
        ],
        Field(
            ...,
            description="One of the six attributes n3IwfId, gNbIdm, ngeNbId, wagfId, tngfId, eNbId shall be present.\n",
        ),
    ]


Tac = Annotated[
    str,
    Field(
        ...,
        pattern=r"(^[A-Fa-f0-9]{4}$)|(^[A-Fa-f0-9]{6}$)",
        description='2 or 3-octet string identifying a tracking area code as specified in clause 9.3.3.10  of 3GPP TS 38.413, in hexadecimal representation. Each character in the string shall  take a value of "0" to "9", "a" to "f" or "A" to "F" and shall represent 4 bits. The most significant character representing the 4 most significant bits of the TAC shall  appear first in the string, and the character representing the 4 least significant bit  of the TAC shall appear last in the string. \n',
    ),
]


class Tai(BaseModel):
    plmnId: PlmnId
    tac: Tac
    nid: Nid | None = None


class NetworkAreaInfo(BaseModel):
    ecgis: list[Ecgi] | None = Field(
        None, description="Contains a list of E-UTRA cell identities.", min_length=1
    )
    ncgis: list[Ncgi] | None = Field(
        None, description="Contains a list of NR cell identities.", min_length=1
    )
    gRanNodeIds: list[GlobalRanNodeId] | None = Field(
        None, description="Contains a list of NG RAN nodes.", min_length=1
    )
    tais: list[Tai] | None = Field(
        None, description="Contains a list of tracking area identities.", min_length=1
    )


DurationSec = Annotated[int, Field(..., description="indicating a time in seconds.")]


ApplicationId = Annotated[
    str, Field(..., description="String providing an application identifier.")
]


Dnn = Annotated[
    str,
    Field(
        ...,
        description='String representing a Data Network as defined in clause 9A of 3GPP TS 23.003;  it shall contain either a DNN Network Identifier, or a full DNN with both the Network  Identifier and Operator Identifier, as specified in 3GPP TS 23.003 clause 9.1.1 and 9.1.2. It shall be coded as string in which the labels are separated by dots  (e.g. "Label1.Label2.Label3").\n',
    ),
]

Dnai = Annotated[
    str,
    Field(
        ...,
        description="DNAI (Data network access identifier), see clause 5.6.7 of 3GPP TS 23.501.",
    ),
]


class E2eDataVolTransTimeCriterion(Enum):
    """Represents the ordering criterion for the list of E2E data volume transfer time.  \nPossible values are:  \n  - E2E_DATA_VOL_TRANS_TIME: The ordering criterion is the E2E data volume transfer time.\n"""

    E2E_DATA_VOL_TRANS_TIME = "E2E_DATA_VOL_TRANS_TIME"


class MatchingDirection(Enum):
    """Represents the matching direction when crossing a threshold.  \nPossible values are:\n- ASCENDING: Threshold is crossed in ascending direction.\n- DESCENDING: Threshold is crossed in descending direction.\n- CROSSED: Threshold is crossed either in ascending or descending direction.\n"""

    ASCENDING = "ASCENDING"
    DESCENDING = "DESCENDING"
    CROSSED = "CROSSED"


Volume = Annotated[
    int,
    Field(
        ...,
        ge=0,
        description="Unsigned integer identifying a volume in units of bytes.",
    ),
]


class DataVolume1(BaseModel):
    uplinkVolume: Volume
    downlinkVolume: Volume | None = None


class DataVolume2(BaseModel):
    uplinkVolume: Volume | None = None
    downlinkVolume: Volume


class DataVolume(RootModel[Union[DataVolume1, DataVolume2]]):
    root: Annotated[
        Union[DataVolume1, DataVolume2],
        Field(..., description="Data Volume including UL/DL."),
    ]


class E2eDataVolTransTimeReq1(BaseModel):
    criterion: E2eDataVolTransTimeCriterion | None = None
    order: MatchingDirection | None = None
    highTransTmThr: Uinteger | None = None
    lowTransTmThr: Uinteger | None = None
    repeatDataTrans: Uinteger
    tsIntervalDataTrans: DurationSec | None = None
    dataVolume: DataVolume | None = None
    maxNumberUes: Uinteger | None = None


class E2eDataVolTransTimeReq2(BaseModel):
    criterion: E2eDataVolTransTimeCriterion | None = None
    order: MatchingDirection | None = None
    highTransTmThr: Uinteger | None = None
    lowTransTmThr: Uinteger | None = None
    repeatDataTrans: Uinteger | None = None
    tsIntervalDataTrans: DurationSec
    dataVolume: DataVolume | None = None
    maxNumberUes: Uinteger | None = None


class E2eDataVolTransTimeReq(
    RootModel[Union[E2eDataVolTransTimeReq1, E2eDataVolTransTimeReq2]]
):
    root: Annotated[
        Union[E2eDataVolTransTimeReq1, E2eDataVolTransTimeReq2],
        Field(
            ...,
            description="Represents other E2E data volume transfer time analytics requirements.",
        ),
    ]


class ExceptionId(Enum):
    """Describes the Exception Id.  \nPossible values are:\n- UNEXPECTED_UE_LOCATION: Unexpected UE location.\n- UNEXPECTED_LONG_LIVE_FLOW: Unexpected long-live rate flows.\n- UNEXPECTED_LARGE_RATE_FLOW: Unexpected large rate flows.\n- UNEXPECTED_WAKEUP: Unexpected wakeup.\n- SUSPICION_OF_DDOS_ATTACK: Suspicion of DDoS attack.\n- WRONG_DESTINATION_ADDRESS: Wrong destination address.\n- TOO_FREQUENT_SERVICE_ACCESS: Too frequent Service Access.\n- UNEXPECTED_RADIO_LINK_FAILURES: Unexpected radio link failures.\n- PING_PONG_ACROSS_CELLS: Ping-ponging across neighbouring cells.\n"""

    UNEXPECTED_UE_LOCATION = "UNEXPECTED_UE_LOCATION"
    UNEXPECTED_LONG_LIVE_FLOW = "UNEXPECTED_LONG_LIVE_FLOW"
    UNEXPECTED_LARGE_RATE_FLOW = "UNEXPECTED_LARGE_RATE_FLOW"
    UNEXPECTED_WAKEUP = "UNEXPECTED_WAKEUP"
    SUSPICION_OF_DDOS_ATTACK = "SUSPICION_OF_DDOS_ATTACK"
    WRONG_DESTINATION_ADDRESS = "WRONG_DESTINATION_ADDRESS"
    TOO_FREQUENT_SERVICE_ACCESS = "TOO_FREQUENT_SERVICE_ACCESS"
    UNEXPECTED_RADIO_LINK_FAILURES = "UNEXPECTED_RADIO_LINK_FAILURES"
    PING_PONG_ACROSS_CELLS = "PING_PONG_ACROSS_CELLS"


class ExceptionTrend(Enum):
    """Represents the Exception Trend.  \nPossible values are:\n- UP: Up trend of the exception level.\n- DOWN: Down trend of the exception level.\n- UNKNOW: Unknown trend of the exception level.\n- STABLE: Stable trend of the exception level.\n"""

    UP = "UP"
    DOWN = "DOWN"
    UNKNOW = "UNKNOW"
    STABLE = "STABLE"


class Exception(BaseModel):
    excepId: ExceptionId
    excepLevel: int | None = None
    excepTrend: ExceptionTrend | None = None


class ExpectedAnalyticsType(Enum):
    """Represents the expected UE analytics type.  \nPossible values are:\n- MOBILITY: Mobility related abnormal behaviour analytics is expected by the consumer.\n- COMMUN: Communication related abnormal behaviour analytics is expected by the consumer.\n- MOBILITY_AND_COMMUN: Both mobility and communication related abnormal behaviour analytics\n  is expected by the consumer.\n"""

    MOBILITY = "MOBILITY"
    COMMUN = "COMMUN"
    MOBILITY_AND_COMMUN = "MOBILITY_AND_COMMUN"


class StationaryIndication(Enum):
    """Possible values are:\n- STATIONARY: Identifies the UE is stationary\n- MOBILE: Identifies the UE is mobile\n"""

    STATIONARY = "STATIONARY"
    MOBILE = "MOBILE"


DayOfWeek = Annotated[
    int,
    Field(
        ...,
        ge=1,
        le=7,
        description="integer between and including 1 and 7 denoting a weekday. 1 shall indicate Monday, and the subsequent weekdays shall be indicated with the next higher numbers. 7 shall indicate Sunday.\n",
    ),
]

TimeOfDay = Annotated[
    str,
    Field(
        ...,
        description="String with format partial-time or full-time as defined in clause 5.6 of IETF RFC 3339. Examples, 20:15:00, 20:15:00-08:00 (for 8 hours behind UTC). \n",
    ),
]


class ScheduledCommunicationTime(BaseModel):
    daysOfWeek: list[DayOfWeek] | None = Field(
        None,
        description="Identifies the day(s) of the week. If absent, it indicates every day of the week.\n",
        max_length=6,
        min_length=1,
    )
    timeOfDayStart: TimeOfDay | None = None
    timeOfDayEnd: TimeOfDay | None = None


class ScheduledCommunicationType(Enum):
    """Possible values are:\n-DOWNLINK_ONLY: Downlink only\n-UPLINK_ONLY: Uplink only\n-BIDIRECTIONA: Bi-directional\n"""

    DOWNLINK_ONLY = "DOWNLINK_ONLY"
    UPLINK_ONLY = "UPLINK_ONLY"
    BIDIRECTIONAL = "BIDIRECTIONAL"


class UmtTime(BaseModel):
    timeOfDay: TimeOfDay
    dayOfWeek: DayOfWeek


class TrafficProfile(Enum):
    """Possible values are:\n- SINGLE_TRANS_UL: Uplink single packet transmission.\n- SINGLE_TRANS_DL: Downlink single packet transmission.\n- DUAL_TRANS_UL_FIRST: Dual packet transmission, firstly uplink packet transmission\n  with subsequent downlink packet transmission.\n- DUAL_TRANS_DL_FIRST: Dual packet transmission, firstly downlink packet transmission\n  with subsequent uplink packet transmission. \n"""

    SINGLE_TRANS_UL = "SINGLE_TRANS_UL"
    SINGLE_TRANS_DL = "SINGLE_TRANS_DL"
    DUAL_TRANS_UL_FIRST = "DUAL_TRANS_UL_FIRST"
    DUAL_TRANS_DL_FIRST = "DUAL_TRANS_DL_FIRST"
    MULTI_TRANS = "MULTI_TRANS"


class BatteryIndication(BaseModel):
    batteryInd: bool | None = Field(
        None,
        description="This IE shall indicate whether the UE is battery powered or not. true: the UE is battery powered; false or absent: the UE is not battery powered\n",
    )
    replaceableInd: bool | None = Field(
        None,
        description="This IE shall indicate whether the battery of the UE is replaceable or not. true: the battery of the UE is replaceable; false or absent: the battery of the UE is not replaceable.\n",
    )
    rechargeableInd: bool | None = Field(
        None,
        description="This IE shall indicate whether the battery of the UE is rechargeable or not. true: the battery of UE is rechargeable; false or absent: the battery of the UE is not rechargeable.\n",
    )


DateTime = Annotated[
    AwareDatetime,
    Field(..., description="string with format 'date-time' as defined in OpenAPI."),
]


BitRate = Annotated[
    str,
    Field(
        ...,
        pattern=r"^\d+(\.\d+)? (bps|Kbps|Mbps|Gbps|Tbps)$",
        description='String representing a bit rate; the prefixes follow the standard symbols from The International System of Units, and represent x1000 multipliers, with the exception that prefix "K" is used to represent the standard symbol "k".\n',
    ),
]

PacketDelBudget = Annotated[
    int,
    Field(
        ...,
        ge=1,
        description="Unsigned integer indicating Packet Delay Budget (see clauses 5.7.3.4 and 5.7.4 of 3GPP TS 23.501), expressed in milliseconds.\n",
    ),
]

PacketLossRate = Annotated[
    int,
    Field(
        ...,
        ge=0,
        le=1000,
        description="Unsigned integer indicating Packet Loss Rate (see clauses 5.7.2.8 and 5.7.4 of 3GPP TS 23.501), expressed in tenth of percent.\n",
    ),
]


class ThresholdLevel(BaseModel):
    congLevel: int | None = None
    nfLoadLevel: int | None = None
    nfCpuUsage: int | None = None
    nfMemoryUsage: int | None = None
    nfStorageUsage: int | None = None
    avgTrafficRate: BitRate | None = None
    maxTrafficRate: BitRate | None = None
    minTrafficRate: BitRate | None = None
    aggTrafficRate: BitRate | None = None
    varTrafficRate: float | None = None
    avgPacketDelay: PacketDelBudget | None = None
    maxPacketDelay: PacketDelBudget | None = None
    varPacketDelay: float | None = None
    avgPacketLossRate: PacketLossRate | None = None
    maxPacketLossRate: PacketLossRate | None = None
    varPacketLossRate: float | None = None
    svcExpLevel: float | None = None
    speed: float | None = None


class Snssai(BaseModel):
    sst: Annotated[
        int,
        Field(
            ...,
            ge=0,
            le=255,
            description="Unsigned integer, within the range 0 to 255, representing the Slice/Service Type.  It indicates the expected Network Slice behaviour in terms of features and services. Values 0 to 127 correspond to the standardized SST range. Values 128 to 255 correspond  to the Operator-specific range. See clause 28.4.2 of 3GPP TS 23.003. Standardized values are defined in clause 5.15.2.2 of 3GPP TS 23.501. \n",
        ),
    ]
    sd: Annotated[
        Optional[str],
        Field(
            pattern=r"^[A-Fa-f0-9]{6}$",
            description='3-octet string, representing the Slice Differentiator, in hexadecimal representation. Each character in the string shall take a value of "0" to "9", "a" to "f" or "A" to "F" and shall represent 4 bits. The most significant character representing the 4 most significant bits of the SD shall appear first in the string, and the character representing the 4 least significant bit of the SD shall appear last in the string. This is an optional parameter that complements the Slice/Service type(s) to allow to  differentiate amongst multiple Network Slices of the same Slice/Service type. This IE shall be absent if no SD value is associated with the SST.\n',
        ),
    ] = None


NsiId = Annotated[
    str,
    Field(
        ...,
        description="Contains the Identifier of the selected Network Slice instance",
    ),
]


class NsiIdInfo(BaseModel):
    snssai: Snssai
    nsiIds: list[NsiId] | None = Field(None, min_length=1)


Field5Qi = Annotated[
    int,
    Field(
        ...,
        ge=0,
        le=255,
        description="Unsigned integer representing a 5G QoS Identifier (see clause 5.7.2.1 of 3GPP TS 23.501, within the range 0 to 255.\n",
    ),
]


class QosResourceType(Enum):
    """The enumeration QosResourceType indicates whether a QoS Flow is non-GBR, delay critical GBR, or non-delay critical GBR (see clauses 5.7.3.4 and 5.7.3.5 of 3GPP TS 23.501). It shall comply with the provisions defined in table 5.5.3.6-1. \n"""

    NON_GBR = "NON_GBR"
    NON_CRITICAL_GBR = "NON_CRITICAL_GBR"
    CRITICAL_GBR = "CRITICAL_GBR"


PacketErrRate = Annotated[
    str,
    Field(
        ...,
        pattern=r"^([0-9]E-[0-9])$",
        description='String representing Packet Error Rate (see clause 5.7.3.5 and 5.7.4 of 3GPP TS 23.501, expressed as a "scalar x 10-k" where the scalar and the exponent k are each encoded as one decimal digit.\n',
    ),
]

HorizontalSpeed = Annotated[
    float,
    Field(..., ge=0.0, le=2047.0, description="Indicates value of horizontal speed."),
]


class HorizontalVelocity(BaseModel):
    hSpeed: HorizontalSpeed
    bearing: Angle


VerticalSpeed = Annotated[
    float,
    Field(..., ge=0.0, le=255.0, description="Indicates value of vertical speed."),
]


class VerticalDirection(Enum):
    UPWARD = "UPWARD"
    DOWNWARD = "DOWNWARD"


class HorizontalWithVerticalVelocity(BaseModel):
    hSpeed: HorizontalSpeed
    bearing: Angle
    vSpeed: VerticalSpeed
    vDirection: VerticalDirection


SpeedUncertainty = Annotated[
    float,
    Field(..., ge=0.0, le=255.0, description="Indicates value of speed uncertainty."),
]


class HorizontalVelocityWithUncertainty(BaseModel):
    hSpeed: HorizontalSpeed
    bearing: Angle
    hUncertainty: SpeedUncertainty


class HorizontalWithVerticalVelocityAndUncertainty(BaseModel):
    hSpeed: HorizontalSpeed
    bearing: Angle
    vSpeed: VerticalSpeed
    vDirection: VerticalDirection
    hUncertainty: SpeedUncertainty
    vUncertainty: SpeedUncertainty


class UnitsLinearVelocity(Enum):
    """The the units of linear velocity."""

    MPERS = "MPERS"
    CMPERS = "CMPERS"


RadialVelocityValue = Annotated[
    int,
    Field(
        ...,
        ge=-2048,
        le=2047,
        description="Indicates value of rate of change of a range between the device A and device B.",
    ),
]

RadialVelocityUncertainty = Annotated[
    int,
    Field(
        ...,
        ge=0,
        le=255,
        description="Indicates uncertainty for rate of change of an range.",
    ),
]


class RadialVelocity(BaseModel):
    unitsRadialVelocity: UnitsLinearVelocity
    radialVelocity: RadialVelocityValue
    rVelocityUncertainty: RadialVelocityUncertainty


class UnitsAngularVelocity(Enum):
    """The units of angular velocity."""

    DEGPERSEC1 = "DEGPERSEC1"
    DEGPERSEC01 = "DEGPERSEC01"


AngularVelocityValue = Annotated[
    int,
    Field(..., ge=-1024, le=1023, description="Indicates rate of change of an angle."),
]

AngularVelocityUncertainty = Annotated[
    int,
    Field(
        ...,
        ge=0,
        le=255,
        description="Indicates uncertainty for rate of change of an angle.",
    ),
]


class AngularVelocity(BaseModel):
    unitsAngularVelocity: UnitsAngularVelocity
    angularVelocity: AngularVelocityValue
    aVelocityUncertainty: AngularVelocityUncertainty


class RelativeVelocityWithUncertainty(BaseModel):
    rVelocity: RadialVelocity | None = None
    aTransverseVelocity: AngularVelocity | None = None
    eTransverseVelocity: AngularVelocity | None = None


class VelocityEstimate(
    RootModel[
        Union[
            HorizontalVelocity,
            HorizontalWithVerticalVelocity,
            HorizontalVelocityWithUncertainty,
            HorizontalWithVerticalVelocityAndUncertainty,
            RelativeVelocityWithUncertainty,
        ]
    ]
):
    root: Annotated[
        Union[
            HorizontalVelocity,
            HorizontalWithVerticalVelocity,
            HorizontalVelocityWithUncertainty,
            HorizontalWithVerticalVelocityAndUncertainty,
            RelativeVelocityWithUncertainty,
        ],
        Field(..., description="Velocity estimate."),
    ]


class DeviceType(Enum):
    """Represents the device type.  \nPossible values are:  \n  - MOBILE_PHONE: Mobile Phone.\n  - SMART_PHONE: Smartphone.\n  - TABLET: Tablet.\n  - DONGLE: Dongle.\n  - MODEM: Modem.\n  - WLAN_ROUTER: WLAN Router.\n  - IOT_DEVICE: IoT Device.\n  - WEARABLE: Wearable.\n  - MOBILE_TEST_PLATFORM: Mobile Test Platform.\n  - UNDEFINED: Undefined.\n"""

    MOBILE_PHONE = "MOBILE_PHONE"
    SMART_PHONE = "SMART_PHONE"
    TABLET = "TABLET"
    DONGLE = "DONGLE"
    MODEM = "MODEM"
    WLAN_ROUTER = "WLAN_ROUTER"
    IOT_DEVICE = "IOT_DEVICE"
    WEARABLE = "WEARABLE"
    MOBILE_TEST_PLATFORM = "MOBILE_TEST_PLATFORM"
    UNDEFINED = "UNDEFINED"


class QosRequirement1(BaseModel):
    field_5qi: Field5Qi = Field(..., alias="5qi")
    gfbrUl: BitRate | None = None
    gfbrDl: BitRate | None = None
    resType: QosResourceType | None = None
    pdb: PacketDelBudget | None = None
    per: PacketErrRate | None = None
    deviceSpeed: VelocityEstimate | None = None
    deviceType: DeviceType | None = None


class QosRequirement2(BaseModel):
    field_5qi: Field5Qi | None = Field(None, alias="5qi")
    gfbrUl: BitRate | None = None
    gfbrDl: BitRate | None = None
    resType: QosResourceType
    pdb: PacketDelBudget | None = None
    per: PacketErrRate | None = None
    deviceSpeed: VelocityEstimate | None = None
    deviceType: DeviceType | None = None


class QosRequirement(RootModel[Union[QosRequirement1, QosRequirement2]]):
    root: Annotated[
        Union[QosRequirement1, QosRequirement2],
        Field(..., description="Represents the QoS requirements."),
    ]


class TimeUnit(Enum):
    """Represents the unit for the session active time.  \nPossible values are:\n- MINUTE: Time unit is per minute.\n- HOUR: Time unit is per hour.\n- DAY: Time unit is per day.\n"""

    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"


class RetainabilityThreshold1(BaseModel):
    relFlowNum: Uinteger
    relTimeUnit: TimeUnit
    relFlowRatio: SamplingRatio | None = None


class RetainabilityThreshold2(BaseModel):
    relFlowNum: Uinteger | None = None
    relTimeUnit: TimeUnit | None = None
    relFlowRatio: SamplingRatio


class RetainabilityThreshold(
    RootModel[Union[RetainabilityThreshold1, RetainabilityThreshold2]]
):
    root: Annotated[
        Union[RetainabilityThreshold1, RetainabilityThreshold2],
        Field(..., description="Represents a QoS flow retainability threshold."),
    ]


class DispersionType(Enum):
    """Represents the dispersion type.  \nPossible values are:\n  - DVDA: Data Volume Dispersion Analytics.\n  - TDA: Transactions Dispersion Analytics.\n  - DVDA_AND_TDA: Data Volume Dispersion Analytics and Transactions Dispersion Analytics.\n"""

    DVDA = "DVDA"
    TDA = "TDA"
    DVDA_AND_TDA = "DVDA_AND_TDA"


class DispersionClass(Enum):
    """Represents the dispersion class.  \nPossible values are:\n- FIXED: Dispersion class as fixed UE its data or transaction usage at a location or\n  a slice, is higher than its class threshold set for its all data or transaction usage.\n- CAMPER: Dispersion class as camper UE, its data or transaction usage at a location or\n  a slice, is higher than its class threshold and lower than the fixed class threshold set\n  for its all data or transaction usage.\n- TRAVELLER: Dispersion class as traveller UE, its data or transaction usage at a location\n  or a slice, is lower than the camper class threshold set for its all data or transaction\n  usage.\n- TOP_HEAVY: Dispersion class as Top_Heavy UE, who's dispersion percentile rating at a\n  location or a slice, is higher than its class threshold.\n"""

    FIXED = "FIXED"
    CAMPER = "CAMPER"
    TRAVELLER = "TRAVELLER"
    TOP_HEAVY = "TOP_HEAVY"


class ClassCriterion(BaseModel):
    disperClass: DispersionClass
    classThreshold: SamplingRatio
    thresMatch: MatchingDirection


class RankingCriterion(BaseModel):
    highBase: SamplingRatio
    lowBase: SamplingRatio


class DispersionOrderingCriterion(Enum):
    """Represents the order criterion for the list of dispersion.  \nPossible values are:\n- TIME_SLOT_START: Indicates the order of time slot start.\n- DISPERSION: Indicates the order of data/transaction dispersion.\n- CLASSIFICATION: Indicates the order of data/transaction classification.\n- RANKING: Indicates the order of data/transaction ranking.\n- PERCENTILE_RANKING: Indicates the order of data/transaction percentile ranking.\n"""

    TIME_SLOT_START = "TIME_SLOT_START"
    DISPERSION = "DISPERSION"
    CLASSIFICATION = "CLASSIFICATION"
    RANKING = "RANKING"
    PERCENTILE_RANKING = "PERCENTILE_RANKING"


class DispersionRequirement(BaseModel):
    disperType: DispersionType
    classCriters: list[ClassCriterion] | None = Field(None, min_length=1)
    rankCriters: list[RankingCriterion] | None = Field(None, min_length=1)
    dispOrderCriter: DispersionOrderingCriterion | None = None
    order: MatchingDirection | None = None


class AnalyticsSubset(Enum):
    """Represents the analytics subset.  \nPossible values are:\n- NUM_OF_UE_REG: The number of UE registered. This value is only applicable to\n  NSI_LOAD_LEVEL event.\n- NUM_OF_PDU_SESS_ESTBL: The number of PDU sessions established. This value is only\n  applicable to NSI_LOAD_LEVEL event.\n- RES_USAGE: The current usage of the virtual resources assigned to the NF instances\n  belonging to a particular network slice instance. This value is only applicable to\n  NSI_LOAD_LEVEL event.\n- NUM_OF_EXCEED_RES_USAGE_LOAD_LEVEL_THR: The number of times the resource usage threshold\n  of the network slice instance is reached or exceeded if a threshold value is provided by\n  the consumer. This value is only applicable to NSI_LOAD_LEVEL event.\n- PERIOD_OF_EXCEED_RES_USAGE_LOAD_LEVEL_THR: The time interval between each time the\n  threshold being met or exceeded on the network slice (instance). This value is only\n  applicable to NSI_LOAD_LEVEL event.\n- EXCEED_LOAD_LEVEL_THR_IND: Whether the Load Level Threshold is met or exceeded by the\n  statistics value. This value is only applicable to NSI_LOAD_LEVEL event.\n- LIST_OF_TOP_APP_UL: The list of applications that contribute the most to the traffic in\n  the UL direction. This value is only applicable to USER_DATA_CONGESTION event.\n- LIST_OF_TOP_APP_DL: The list of applications that contribute the most to the traffic in\n  the DL direction. This value is only applicable to USER_DATA_CONGESTION event.\n- NF_STATUS: The availability status of the NF on the Analytics target period, expressed\n  as a percentage of time per status value (registered, suspended, undiscoverable). This\n  value is only applicable to NF_LOAD event.\n- NF_RESOURCE_USAGE: The average usage of assigned resources (CPU, memory, storage). This\n  value is only applicable to NF_LOAD event.\n- NF_LOAD: The average load of the NF instance over the Analytics target period. This value\n  is only applicable to NF_LOAD event.\n- NF_PEAK_LOAD: The maximum load of the NF instance over the Analytics target period. This\n  value is only applicable to NF_LOAD event.\n- NF_LOAD_AVG_IN_AOI: The average load of the NF instances over the area of interest. This\n  value is only applicable to NF_LOAD event.\n- DISPER_AMOUNT: Indicates the dispersion amount of the reported data volume or transaction\n  dispersion type. This value is only applicable to DISPERSION event.\n- DISPER_CLASS: Indicates the dispersion mobility class: fixed, camper, traveller upon set\n  its usage threshold, and/or the top-heavy class upon set its percentile rating threshold.\n  This value is only applicable to DISPERSION event.\n- RANKING: Data/transaction usage ranking high (i.e.value 1), medium (2) or low (3). This\n  value is only applicable to DISPERSION event.\n- PERCENTILE_RANKING: Percentile ranking of the target UE in the Cumulative Distribution\n  Function of data usage for the population of all UEs. This value is only applicable to\n  DISPERSION event.\n- RSSI: Indicated the RSSI in the unit of dBm. This value is only applicable to\n  WLAN_PERFORMANCE event.\n- RTT: Indicates the RTT in the unit of millisecond. This value is only applicable to\n  WLAN_PERFORMANCE event.\n- TRAFFIC_INFO: Traffic information including UL/DL data rate and/or Traffic volume. This\n  value is only applicable to WLAN_PERFORMANCE event.\n- NUMBER_OF_UES: Number of UEs observed for the SSID. This value is only applicable to\n  WLAN_PERFORMANCE event.\n- APP_LIST_FOR_UE_COMM: The analytics of the application list used by UE. This value is only\n  applicable to UE_COMMUNICATION event.\n- N4_SESS_INACT_TIMER_FOR_UE_COMM: The N4 Session inactivity timer. This value is only\n  applicable to UE_COMMUNICATION event.\n- AVG_TRAFFIC_RATE: Indicates average traffic rate. This value is only applicable to\n  DN_PERFORMANCE event.\n- MAX_TRAFFIC_RATE: Indicates maximum traffic rate. This value is only applicable to\n  DN_PERFORMANCE event.\n- AGG_TRAFFIC_RATE: Indicates aggregated traffic rate. This value is only applicable to\n  DN_PERFORMANCE event.\n- VAR_TRAFFIC_RATE: Indicates variance traffic rate. This value is only applicable to\n  DN_PERFORMANCE event.\n- AVG_PACKET_DELAY: Indicates average Packet Delay. This value is only applicable to\n  DN_PERFORMANCE event.\n- MAX_PACKET_DELAY: Indicates maximum Packet Delay. This value is only applicable to\n  DN_PERFORMANCE event.\n- VAR_PACKET_DELAY: Indicates variance Packet Delay. This value is only applicable to\n  DN_PERFORMANCE event.\n- AVG_PACKET_LOSS_RATE: Indicates average Loss Rate. This value is only applicable to\n  DN_PERFORMANCE event.\n- MAX_PACKET_LOSS_RATE: Indicates maximum Packet Loss Rate. This value is only applicable to\n  DN_PERFORMANCE event.\n- VAR_PACKET_LOSS_RATE: Indicates variance Packet Loss Rate. This value is only applicable\n  to DN_PERFORMANCE event.\n- UE_LOCATION: Indicates UE location information. This value is only applicable to\n  SERVICE_EXPERIENCE event.\n- LIST_OF_HIGH_EXP_UE: Indicates list of high experienced UE. This value is only applicable\n  to SM_CONGESTION event.\n- LIST_OF_MEDIUM_EXP_UE: Indicates list of medium experienced UE. This value is only\n  applicable to SM_CONGESTION event.\n- LIST_OF_LOW_EXP_UE: Indicates list of low experienced UE. This value is only applicable to\n  SM_CONGESTION event.\n- AVG_UL_PKT_DROP_RATE: Indicates average uplink packet drop rate on GTP-U path on N3. This\n  value is only applicable to RED_TRANS_EXP event.\n- VAR_UL_PKT_DROP_RATE: Indicates variance of uplink packet drop rate on GTP-U path on N3.\n  This value is only applicable to RED_TRANS_EXP event.\n- AVG_DL_PKT_DROP_RATE: Indicates average downlink packet drop rate on GTP-U path on N3.\n  This value is only applicable to RED_TRANS_EXP event.\n- VAR_DL_PKT_DROP_RATE: Indicates variance of downlink packet drop rate on GTP-U path on N3.\n  This value is only applicable to RED_TRANS_EXP event.\n- AVG_UL_PKT_DELAY: Indicates average uplink packet delay round trip on GTP-U path on N3.\n  This value is only applicable to RED_TRANS_EXP event.\n- VAR_UL_PKT_DELAY: Indicates variance uplink packet delay round trip on GTP-U path on N3.\n  This value is only applicable to RED_TRANS_EXP event.\n- AVG_DL_PKT_DELAY: Indicates average downlink packet delay round trip on GTP-U path on N3.\n  This value is only applicable to RED_TRANS_EXP event.\n- VAR_DL_PKT_DELAY: Indicates variance downlink packet delay round trip on GTP-U path on N3.\n  This value is only applicable to RED_TRANS_EXP event.\n- TRAFFIC_MATCH_TD: Identifies traffic that matches Traffic Descriptor provided by\n  the consumer.\n- TRAFFIC_UNMATCH_TD: Identifies traffic that does not match Traffic Descriptor\n  provided by the consumer.\n- NUMBER_OF_UE: Indicates the number of UEs. This value is only applicable to\n  DN_PERFORMANCE event.\n- UE_GEOG_DIST: Indicates the geographical distribution of the UEs that can be selected by\n  the AF for application service. This value is only applicable to UE_MOBILITY event.\n- UE_DIRECTION: Indicates the direction of the UEs. This value is only applicable to\n  UE_MOBILITY event.\n- AVG_E2E_UL_PKT_DELAY: Indicates average End-to-End (between UE and UPF) uplink packet\n  delay. This value is only applicable to RED_TRANS_EXP event.\n- VAR_E2E_UL_PKT_DELAY: Indicates the variance of End-to-End (between UE and UPF) uplink\n  packet delay. This value is only applicable to RED_TRANS_EXP event.\n- AVG_E2E_DL_PKT_DELAY: Indicates average End-to-End (between UE and UPF) downlink packet\n  delay. This value is only applicable to RED_TRANS_EXP event.\n- VAR_E2E_DL_PKT_DELAY: Indicates the variance of End-to-End (between UE and UPF) downlink\n  packet delay. This value is only applicable to RED_TRANS_EXP event.\n- AVG_E2E_UL_PKT_LOSS_RATE: Indicates average End-to-End (between UE and UPF) uplink packet\n  loss rate. This value is only applicable to RED_TRANS_EXP event.\n- VAR_E2E_UL_PKT_LOSS_RATE: Indicates the variance of End-to-End (between UE and UPF) uplink\n  packet loss rate. This value is only applicable to RED_TRANS_EXP event.\n- AVG_E2E_DL_PKT_LOSS_RATE: Indicates average End-to-End (between UE and UPF) downlink\n  packet loss rate. This value is only applicable to RED_TRANS_EXP event.\n- VAR_E2E_DL_PKT_LOSS_RATE: Indicates the variance of End-to-End (between UE and UPF)\n  downlink packet loss rate. This value is only applicable to RED_TRANS_EXP event.\n- E2E_DATA_VOL_TRANS_TIME_FOR_UE_LIST: Indicates the classified E2E data volume transfer\n  time statistics or predictions for multiple UEs with respect to one or more reporting\n  thresholds.\n- NUM_OF_UE: Indicates the total number of users in the area of interest. This\n  value is only applicable to MOVEMENT_BEHAVIOUR event.\n- MOV_UE_RATIO: Indicates the Ratio of moving UEs in the area of interest. This value\n  is only applicable to MOVEMENT_BEHAVIOUR event.\n- AVR_SPEED: Indicates the average speed of all UEs in the area of interest. This value\n  is only applicable to MOVEMENT_BEHAVIOUR event.\n- SPEED_THRESHOLD: Indicates the information on UEs in the area of interest whose speed\n  is faster than the speed threshold. This value is only applicable to MOVEMENT_BEHAVIOUR\n  event.\n- MOV_UE_DIRECTION: Indicates the heading directions of the UE flow in the target area.\n  This value is only applicable to MOVEMENT_BEHAVIOUR event.\n- IN_OUT_PERCENT: Indicates the percentage of indoor/outdoor UEs at a location.\n  The value is only applicable to the LOC_ACCURACY event.\n- TIME_TO_COLLISION: Indicates the time until for a collision with another UE happens.\n  This value is only applicable to RELATIVE_PROXIMITY event prediction.\n"""

    NUM_OF_UE_REG = "NUM_OF_UE_REG"
    NUM_OF_PDU_SESS_ESTBL = "NUM_OF_PDU_SESS_ESTBL"
    RES_USAGE = "RES_USAGE"
    NUM_OF_EXCEED_RES_USAGE_LOAD_LEVEL_THR = "NUM_OF_EXCEED_RES_USAGE_LOAD_LEVEL_THR"
    PERIOD_OF_EXCEED_RES_USAGE_LOAD_LEVEL_THR = (
        "PERIOD_OF_EXCEED_RES_USAGE_LOAD_LEVEL_THR"
    )
    EXCEED_LOAD_LEVEL_THR_IND = "EXCEED_LOAD_LEVEL_THR_IND"
    LIST_OF_TOP_APP_UL = "LIST_OF_TOP_APP_UL"
    LIST_OF_TOP_APP_DL = "LIST_OF_TOP_APP_DL"
    NF_STATUS = "NF_STATUS"
    NF_RESOURCE_USAGE = "NF_RESOURCE_USAGE"
    NF_LOAD = "NF_LOAD"
    NF_PEAK_LOAD = "NF_PEAK_LOAD"
    NF_LOAD_AVG_IN_AOI = "NF_LOAD_AVG_IN_AOI"
    DISPER_AMOUNT = "DISPER_AMOUNT"
    DISPER_CLASS = "DISPER_CLASS"
    RANKING = "RANKING"
    PERCENTILE_RANKING = "PERCENTILE_RANKING"
    RSSI = "RSSI"
    RTT = "RTT"
    TRAFFIC_INFO = "TRAFFIC_INFO"
    NUMBER_OF_UES = "NUMBER_OF_UES"
    APP_LIST_FOR_UE_COMM = "APP_LIST_FOR_UE_COMM"
    N4_SESS_INACT_TIMER_FOR_UE_COMM = "N4_SESS_INACT_TIMER_FOR_UE_COMM"
    AVG_TRAFFIC_RATE = "AVG_TRAFFIC_RATE"
    MAX_TRAFFIC_RATE = "MAX_TRAFFIC_RATE"
    AGG_TRAFFIC_RATE = "AGG_TRAFFIC_RATE"
    VAR_TRAFFIC_RATE = "VAR_TRAFFIC_RATE"
    AVG_PACKET_DELAY = "AVG_PACKET_DELAY"
    MAX_PACKET_DELAY = "MAX_PACKET_DELAY"
    VAR_PACKET_DELAY = "VAR_PACKET_DELAY"
    AVG_PACKET_LOSS_RATE = "AVG_PACKET_LOSS_RATE"
    MAX_PACKET_LOSS_RATE = "MAX_PACKET_LOSS_RATE"
    VAR_PACKET_LOSS_RATE = "VAR_PACKET_LOSS_RATE"
    UE_LOCATION = "UE_LOCATION"
    LIST_OF_HIGH_EXP_UE = "LIST_OF_HIGH_EXP_UE"
    LIST_OF_MEDIUM_EXP_UE = "LIST_OF_MEDIUM_EXP_UE"
    LIST_OF_LOW_EXP_UE = "LIST_OF_LOW_EXP_UE"
    AVG_UL_PKT_DROP_RATE = "AVG_UL_PKT_DROP_RATE"
    VAR_UL_PKT_DROP_RATE = "VAR_UL_PKT_DROP_RATE"
    AVG_DL_PKT_DROP_RATE = "AVG_DL_PKT_DROP_RATE"
    VAR_DL_PKT_DROP_RATE = "VAR_DL_PKT_DROP_RATE"
    AVG_UL_PKT_DELAY = "AVG_UL_PKT_DELAY"
    VAR_UL_PKT_DELAY = "VAR_UL_PKT_DELAY"
    AVG_DL_PKT_DELAY = "AVG_DL_PKT_DELAY"
    VAR_DL_PKT_DELAY = "VAR_DL_PKT_DELAY"
    TRAFFIC_MATCH_TD = "TRAFFIC_MATCH_TD"
    TRAFFIC_UNMATCH_TD = "TRAFFIC_UNMATCH_TD"
    NUMBER_OF_UE = "NUMBER_OF_UE"
    UE_GEOG_DIST = "UE_GEOG_DIST"
    UE_DIRECTION = "UE_DIRECTION"
    AVG_E2E_UL_PKT_DELAY = "AVG_E2E_UL_PKT_DELAY"
    VAR_E2E_UL_PKT_DELAY = "VAR_E2E_UL_PKT_DELAY"
    AVG_E2E_DL_PKT_DELAY = "AVG_E2E_DL_PKT_DELAY"
    VAR_E2E_DL_PKT_DELAY = "VAR_E2E_DL_PKT_DELAY"
    AVG_E2E_UL_PKT_LOSS_RATE = "AVG_E2E_UL_PKT_LOSS_RATE"
    VAR_E2E_UL_PKT_LOSS_RATE = "VAR_E2E_UL_PKT_LOSS_RATE"
    AVG_E2E_DL_PKT_LOSS_RATE = "AVG_E2E_DL_PKT_LOSS_RATE"
    VAR_E2E_DL_PKT_LOSS_RATE = "VAR_E2E_DL_PKT_LOSS_RATE"
    E2E_DATA_VOL_TRANS_TIME_FOR_UE_LIST = "E2E_DATA_VOL_TRANS_TIME_FOR_UE_LIST"
    NUM_OF_UE = "NUM_OF_UE"
    MOV_UE_RATIO = "MOV_UE_RATIO"
    AVR_SPEED = "AVR_SPEED"
    SPEED_THRESHOLD = "SPEED_THRESHOLD"
    MOV_UE_DIRECTION = "MOV_UE_DIRECTION"
    IN_OUT_PERCENT = "IN_OUT_PERCENT"
    TIME_TO_COLLISION = "TIME_TO_COLLISION"


class DnPerfOrderingCriterion(Enum):
    """Represents the order criterion for the list of DN performance analytics.  \nPossible values are:  \n- AVERAGE_TRAFFIC_RATE: Indicates the average traffic rate.  \n- MAXIMUM_TRAFFIC_RATE: Indicates the maximum traffic rate.  \n- AVERAGE_PACKET_DELAY: Indicates the average packet delay.  \n- MAXIMUM_PACKET_DELAY: Indicates the maximum packet delay.  \n- AVERAGE_PACKET_LOSS_RATE: Indicates the average packet loss rate.\n"""

    AVERAGE_TRAFFIC_RATE = "AVERAGE_TRAFFIC_RATE"
    MAXIMUM_TRAFFIC_RATE = "MAXIMUM_TRAFFIC_RATE"
    AVERAGE_PACKET_DELAY = "AVERAGE_PACKET_DELAY"
    MAXIMUM_PACKET_DELAY = "MAXIMUM_PACKET_DELAY"
    AVERAGE_PACKET_LOSS_RATE = "AVERAGE_PACKET_LOSS_RATE"


class DnPerformanceReq(BaseModel):
    dnPerfOrderCriter: DnPerfOrderingCriterion | None = None
    order: MatchingDirection | None = None
    reportThresholds: list[ThresholdLevel] | None = Field(None, min_length=1)


class BwRequirement(BaseModel):
    appId: ApplicationId
    marBwDl: BitRate | None = None
    marBwUl: BitRate | None = None
    mirBwDl: BitRate | None = None
    mirBwUl: BitRate | None = None


ArfcnValueNR = Annotated[
    int,
    Field(
        ...,
        ge=0,
        le=3279165,
        description='Integer value indicating the ARFCN applicable for a downlink, uplink or bi-directional (TDD) NR global frequency raster, as definition of "ARFCN-ValueNR" IE in clause 6.3.2 of 3GPP TS 38.331.\n',
    ),
]


class RatType(Enum):
    """Indicates the radio access used."""

    NR = "NR"
    EUTRA = "EUTRA"
    WLAN = "WLAN"
    VIRTUAL = "VIRTUAL"
    NBIOT = "NBIOT"
    WIRELINE = "WIRELINE"
    WIRELINE_CABLE = "WIRELINE_CABLE"
    WIRELINE_BBF = "WIRELINE_BBF"
    LTE_M = "LTE-M"
    NR_U = "NR_U"
    EUTRA_U = "EUTRA_U"
    TRUSTED_N3GA = "TRUSTED_N3GA"
    TRUSTED_WLAN = "TRUSTED_WLAN"
    UTRA = "UTRA"
    GERA = "GERA"
    NR_LEO = "NR_LEO"
    NR_MEO = "NR_MEO"
    NR_GEO = "NR_GEO"
    NR_OTHER_SAT = "NR_OTHER_SAT"
    NR_REDCAP = "NR_REDCAP"
    WB_E_UTRAN_LEO = "WB_E_UTRAN_LEO"
    WB_E_UTRAN_MEO = "WB_E_UTRAN_MEO"
    WB_E_UTRAN_GEO = "WB_E_UTRAN_GEO"
    WB_E_UTRAN_OTHERSAT = "WB_E_UTRAN_OTHERSAT"
    NB_IOT_LEO = "NB_IOT_LEO"
    NB_IOT_MEO = "NB_IOT_MEO"
    NB_IOT_GEO = "NB_IOT_GEO"
    NB_IOT_OTHERSAT = "NB_IOT_OTHERSAT"
    LTE_M_LEO = "LTE_M_LEO"
    LTE_M_MEO = "LTE_M_MEO"
    LTE_M_GEO = "LTE_M_GEO"
    LTE_M_OTHERSAT = "LTE_M_OTHERSAT"
    NR_EREDCAP = "NR_EREDCAP"


class RatFreqInformation(BaseModel):
    allFreq: bool | None = Field(
        None,
        description='Set to "true" to indicate to handle all the frequencies the NWDAF received, otherwise set to "false" or omit. The "allFreq" attribute and the "freq" attribute are mutually exclusive.\n',
    )
    allRat: bool | None = Field(
        None,
        description='Set to "true" to indicate to handle all the RAT Types the NWDAF received, otherwise set to "false" or omit. The "allRat" attribute and the "ratType" attribute are mutually exclusive.\n',
    )
    freq: ArfcnValueNR | None = None
    ratType: RatType | None = None
    svcExpThreshold: ThresholdLevel | None = None
    matchingDir: MatchingDirection | None = None


Ipv4Addr = Annotated[
    str,
    Field(
        ...,
        pattern=r"^(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$",
        description="String identifying a IPv4 address formatted in the 'dotted decimal' notation as defined in RFC 1166.\n",
        examples=["198.51.100.1"],
    ),
]


class Ipv6Addr(BaseModel):
    pass


class Ipv6Prefix(BaseModel):
    pass


class IpAddr1(BaseModel):
    ipv4Addr: Ipv4Addr
    ipv6Addr: Ipv6Addr | None = None
    ipv6Prefix: Ipv6Prefix | None = None


class IpAddr2(BaseModel):
    ipv4Addr: Ipv4Addr | None = None
    ipv6Addr: Ipv6Addr
    ipv6Prefix: Ipv6Prefix | None = None


class IpAddr3(BaseModel):
    ipv4Addr: Ipv4Addr | None = None
    ipv6Addr: Ipv6Addr | None = None
    ipv6Prefix: Ipv6Prefix


class IpAddr(RootModel[Union[IpAddr1, IpAddr2, IpAddr3]]):
    root: Annotated[
        Union[IpAddr1, IpAddr2, IpAddr3],
        Field(..., description="Contains an IP adresse."),
    ]


class AddrFqdn(BaseModel):
    ipAddr: IpAddr | None = None
    fqdn: str | None = Field(None, description="Indicates an FQDN.")


class WlanOrderingCriterion(Enum):
    """Represents the order criterion for the list of WLAN performance information.  \nPossible values are:\n- TIME_SLOT_START: Indicates the order of time slot start.\n- NUMBER_OF_UES: Indicates the order of number of UEs.\n- RSSI: Indicates the order of RSSI.\n- RTT: Indicates the order of RTT.\n- TRAFFIC_INFO: Indicates the order of Traffic information.\n"""

    TIME_SLOT_START = "TIME_SLOT_START"
    NUMBER_OF_UES = "NUMBER_OF_UES"
    RSSI = "RSSI"
    RTT = "RTT"
    TRAFFIC_INFO = "TRAFFIC_INFO"


class WlanPerformanceReq(BaseModel):
    ssIds: list[str] | None = Field(None, min_length=1)
    bssIds: list[str] | None = Field(None, min_length=1)
    wlanOrderCriter: WlanOrderingCriterion | None = None
    order: MatchingDirection | None = None


class Accuracy(Enum):
    """Represents the preferred level of accuracy of the analytics.  \nPossible values are:\n- LOW: Low accuracy.\n- MEDIUM: Medium accuracy.\n- HIGH: High accuracy.\n- HIGHEST: Highest accuracy.\n"""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    HIGHEST = "HIGHEST"


class AnalyticsMetadata(Enum):
    """Represents the types of analytics metadata information that can be requested.  \nPossible values are:\n- NUM_OF_SAMPLES: Number of data samples used for the generation of the output analytics.\n- DATA_WINDOW: Data time window of the data samples.\n- DATA_STAT_PROPS: Dataset statistical properties of the data used to generate the\n  analytics.\n- STRATEGY: Output strategy used for the reporting of the analytics.\n- ACCURACY: Level of accuracy reached for the analytics.\n"""

    NUM_OF_SAMPLES = "NUM_OF_SAMPLES"
    DATA_WINDOW = "DATA_WINDOW"
    DATA_STAT_PROPS = "DATA_STAT_PROPS"
    STRATEGY = "STRATEGY"
    ACCURACY = "ACCURACY"


class TimeWindow(BaseModel):
    startTime: DateTime
    stopTime: DateTime


class DatasetStatisticalProperty(Enum):
    """Represents the dataset statistical properties.  \nPossible values are:\n- UNIFORM_DIST_DATA: Indicates the use of data samples that are uniformly distributed\n  according to the different aspects of the requested analytics.\n- NO_OUTLIERS: Indicates that the data samples shall disregard data samples that are at\n  the extreme boundaries of the value range.\n"""

    UNIFORM_DIST_DATA = "UNIFORM_DIST_DATA"
    NO_OUTLIERS = "NO_OUTLIERS"


class OutputStrategy(Enum):
    """Represents the output strategy used for the analytics reporting.  \nPossible values are:\n- BINARY: Indicates that the analytics shall only be reported when the requested level\n  of accuracy is reached within a cycle of periodic notification.\n- GRADIENT: Indicates that the analytics shall be reported according with the periodicity\n  irrespective of whether the requested level of accuracy has been reached or not.\n"""

    BINARY = "BINARY"
    GRADIENT = "GRADIENT"


NfInstanceId = Annotated[
    UUID,
    Field(
        ...,
        description="String uniquely identifying a NF instance. The format of the NF Instance ID shall be a  Universally Unique Identifier (UUID) version 4, as described in IETF RFC 4122. \n",
    ),
]


class AnalyticsMetadataIndication(BaseModel):
    dataWindow: TimeWindow | None = None
    dataStatProps: list[DatasetStatisticalProperty] | None = Field(None, min_length=1)
    strategy: OutputStrategy | None = None
    aggrNwdafIds: list[NfInstanceId] | None = Field(None, min_length=1)


class EventReportingRequirement(BaseModel):
    accuracy: Accuracy | None = None
    accPerSubset: list[Accuracy] | None = Field(
        None,
        description='Each element indicates the preferred accuracy level per analytics subset. It may be present if the "listOfAnaSubsets" attribute is present in the subscription request.\n',
        min_length=1,
    )
    startTs: DateTime | None = None
    endTs: DateTime | None = None
    offsetPeriod: int | None = Field(
        None,
        description='Offset period in units of seconds to the reporting time, if the value is negative means statistics in the past offset period, otherwise a positive value means prediction in the future offset period. May be present if the "repPeriod" attribute is included within the "evtReq" attribute or the "repetitionPeriod" attribute is included within the EventSubscription type.\n',
    )
    sampRatio: SamplingRatio | None = None
    maxObjectNbr: Uinteger | None = None
    maxSupiNbr: Uinteger | None = None
    timeAnaNeeded: DateTime | None = None
    anaMeta: list[AnalyticsMetadata] | None = Field(None, min_length=1)
    anaMetaInd: AnalyticsMetadataIndication | None = None
    histAnaTimePeriod: TimeWindow | None = None


class PduSessionType(Enum):
    """PduSessionType indicates the type of a PDU session. It shall comply with the provisions defined in table 5.4.3.3-1. \n"""

    IPV4 = "IPV4"
    IPV6 = "IPV6"
    IPV4V6 = "IPV4V6"
    UNSTRUCTURED = "UNSTRUCTURED"
    ETHERNET = "ETHERNET"


class SscMode(Enum):
    """represents the service and session continuity mode It shall comply with the provisions defined in table 5.4.3.6-1. \n"""

    SSC_MODE_1 = "SSC_MODE_1"
    SSC_MODE_2 = "SSC_MODE_2"
    SSC_MODE_3 = "SSC_MODE_3"


class AccessType(Enum):
    field_3GPP_ACCESS = "3GPP_ACCESS"
    NON_3GPP_ACCESS = "NON_3GPP_ACCESS"


class PduSessionInfo(BaseModel):
    pduSessType: PduSessionType | None = None
    sscMode: SscMode | None = None
    accessTypes: list[AccessType] | None = Field(None, min_length=1)


class UeCommOrderCriterion(Enum):
    """Represents the ordering criterion for the list of UE communication analytics.  \nPossible values are:  \n  - START_TIME: The ordering criterion of the analytics is the start time.\n  - DURATION: The ordering criterion of the analytics is the duration of the communication.\n"""

    START_TIME = "START_TIME"
    DURATION = "DURATION"


class UeCommReq(BaseModel):
    orderCriterion: UeCommOrderCriterion | None = None
    orderDirection: MatchingDirection | None = None


class UserDataConOrderCrit(Enum):
    """Represents the cause for requesting to terminate an analytics subscription.  \nPossible values are:  \n  - APPLICABLE_TIME_WINDOW: The ordering criterion is the Applicable Time Window.\n  - NETWORK_STATUS_INDICATION: The ordering criterion is the network status indication.\n"""

    APPLICABLE_TIME_WINDOW = "APPLICABLE_TIME_WINDOW"
    NETWORK_STATUS_INDICATION = "NETWORK_STATUS_INDICATION"


class LocInfoGranularity(Enum):
    """Represents the preferred granularity of location information.  \nPossible values are:  \n  - TA_LEVEL: Indicates location granularity of TA level.\n  - CELL_LEVEL: Indicates location granularity of Cell level.\n  - LON_AND_LAT_LEVEL: Indicates location granularity of longitude and latitude level.\n"""

    TA_LEVEL = "TA_LEVEL"
    CELL_LEVEL = "CELL_LEVEL"
    LON_AND_LAT_LEVEL = "LON_AND_LAT_LEVEL"


class LocationOrientation(Enum):
    """Possible values are:  \n  - HORIZONTAL: Indicates horizontal orientation.\n  - VERTICAL: Indicates vertical orientation.\n  - HOR_AND_VER: Indicates both horizontal and vertical orientation.\n"""

    HORIZONTAL = "HORIZONTAL"
    VERTICAL = "VERTICAL"
    HOR_AND_VER = "HOR_AND_VER"


class UeMobilityOrderCriterion(Enum):
    """Represents the ordering criterion for the list of UE mobility analytics.  \nPossible values are:  \n  - TIME_SLOT: The ordering criterion is the time slot.\n"""

    TIME_SLOT = "TIME_SLOT"


class UeMobilityReq(BaseModel):
    orderCriterion: UeMobilityOrderCriterion | None = None
    orderDirection: MatchingDirection | None = None
    ueLocOrderInd: bool | None = Field(
        None,
        description='UE Location order indication. Set to "true" to indicate the NWDAF to provide UE locations in the UE Mobility analytics in time order, otherwise set to "false" or omitted.\n',
    )
    distThresholds: list[Uinteger] | None = Field(
        None, description="Indicates the linear distance threshold.", min_length=1
    )


class MovBehavReq(BaseModel):
    locationGranReq: LocInfoGranularity | None = None
    reportThresholds: ThresholdLevel | None = None


class Direction(Enum):
    """Possible values are:  \n  - NORTH: North direction.\n  - SOUTH: South direction.\n  - EAST: EAST direction.\n  - WEST: WEST direction.\n  - NORTHWEST: Northwest direction.\n  - NORTHEAST: Northeast direction.\n  - SOUTHWEST: Southwest direction.\n  - SOUTHEAST: Southeast direction.\n"""

    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST = "EAST"
    WEST = "WEST"
    NORTHWEST = "NORTHWEST"
    NORTHEAST = "NORTHEAST"
    SOUTHWEST = "SOUTHWEST"
    SOUTHEAST = "SOUTHEAST"


class ProximityCriterion(Enum):
    """Possible values are:  \n  - VELOCITY: Velocity.\n  - AVG_SPD: Average speed.\n  - ORIENTATION: Orientation.\n  - TRAJECTORY: Mobility trajectory.\n"""

    VELOCITY = "VELOCITY"
    AVG_SPD = "AVG_SPD"
    ORIENTATION = "ORIENTATION"
    TRAJECTORY = "TRAJECTORY"


class RelProxReq(BaseModel):
    direction: list[Direction] | None = Field(None, min_length=1)
    numOfUe: Uinteger | None = None
    proximityCrits: list[ProximityCriterion] | None = Field(None, min_length=1)


class AccuracyReq(BaseModel):
    accuTimeWin: TimeWindow | None = None
    accuPeriod: DurationSec | None = None
    accuDevThr: Uinteger | None = None
    minNum: Uinteger | None = None
    updatedAnaFlg: bool | None = Field(
        None,
        description='Indicates the updated Analytics flag. Set to "true" indicates that the NWDAF can provide the updated analytics if the analytics can be generated within the analytics accuracy information time window, which is specified by "accuTimeWin" attribute. Otherwise set to “false”. Default value is “false” if omitted.\n',
    )
    correctionInterval: DurationSec | None = None


class NwdafEvent(Enum):
    """Describes the NWDAF Events.  \nPossible values are:\n- SLICE_LOAD_LEVEL: Indicates that the event subscribed is load level information of Network\n  Slice.\n- NETWORK_PERFORMANCE: Indicates that the event subscribed is network performance\n  information.\n- NF_LOAD: Indicates that the event subscribed is load level and status of one or several\n  Network Functions.\n- SERVICE_EXPERIENCE: Indicates that the event subscribed is service experience.\n- UE_MOBILITY: Indicates that the event subscribed is UE mobility information.\n- UE_COMMUNICATION: Indicates that the event subscribed is UE communication information.\n- QOS_SUSTAINABILITY: Indicates that the event subscribed is QoS sustainability.\n- ABNORMAL_BEHAVIOUR: Indicates that the event subscribed is abnormal behaviour.\n- USER_DATA_CONGESTION: Indicates that the event subscribed is user data congestion\n  information.\n- NSI_LOAD_LEVEL: Indicates that the event subscribed is load level information of Network\n  Slice and the optionally associated Network Slice Instance.\n- DN_PERFORMANCE: Indicates that the event subscribed is DN performance information.\n- DISPERSION: Indicates that the event subscribed is dispersion information.\n- RED_TRANS_EXP: Indicates that the event subscribed is redundant transmission experience.\n- WLAN_PERFORMANCE: Indicates that the event subscribed is WLAN performance.\n- SM_CONGESTION: Indicates the Session Management Congestion Control Experience information\n  for specific DNN and/or S-NSSAI.\n- PFD_DETERMINATION: Indicates that the event subscribed is the PFD Determination nformation\n  for known application identifier(s).\n- PDU_SESSION_TRAFFIC: Indicates that the event subscribed is the PDU Session traffic\n  information.\n- E2E_DATA_VOL_TRANS_TIME: Indicates that the event subscribed is of E2E data volume \n  transfer time.\n- MOVEMENT_BEHAVIOUR: Indicates that the event subscribed is the Movement Behaviour\n  information.\n- LOC_ACCURACY: Indicates that the event subscribed is of location accuracy.\n- RELATIVE_PROXIMITY: Indicates that the event subscribed is the Relative Proximity\n  information.\n"""

    SLICE_LOAD_LEVEL = "SLICE_LOAD_LEVEL"
    NETWORK_PERFORMANCE = "NETWORK_PERFORMANCE"
    NF_LOAD = "NF_LOAD"
    SERVICE_EXPERIENCE = "SERVICE_EXPERIENCE"
    UE_MOBILITY = "UE_MOBILITY"
    UE_COMMUNICATION = "UE_COMMUNICATION"
    QOS_SUSTAINABILITY = "QOS_SUSTAINABILITY"
    ABNORMAL_BEHAVIOUR = "ABNORMAL_BEHAVIOUR"
    USER_DATA_CONGESTION = "USER_DATA_CONGESTION"
    NSI_LOAD_LEVEL = "NSI_LOAD_LEVEL"
    DN_PERFORMANCE = "DN_PERFORMANCE"
    DISPERSION = "DISPERSION"
    RED_TRANS_EXP = "RED_TRANS_EXP"
    WLAN_PERFORMANCE = "WLAN_PERFORMANCE"
    SM_CONGESTION = "SM_CONGESTION"
    PFD_DETERMINATION = "PFD_DETERMINATION"
    PDU_SESSION_TRAFFIC = "PDU_SESSION_TRAFFIC"
    E2E_DATA_VOL_TRANS_TIME = "E2E_DATA_VOL_TRANS_TIME"
    MOVEMENT_BEHAVIOUR = "MOVEMENT_BEHAVIOUR"
    LOC_ACCURACY = "LOC_ACCURACY"
    RELATIVE_PROXIMITY = "RELATIVE_PROXIMITY"


class AnalyticsFeedbackInfo(BaseModel):
    actionTimes: list[DateTime] = Field(
        ..., description="The times at which an action was taken.", min_length=1
    )
    usedAnaTypes: list[NwdafEvent] | None = Field(
        None,
        description="The analytics types that were used to take the action.",
        min_length=1,
    )
    impactInd: bool | None = Field(
        None,
        description="Indication about the impact of an action on the ground truth data.",
    )


Gpsi = Annotated[
    str,
    Field(
        ...,
        pattern=r"^(msisdn-[0-9]{5,15}|extid-[^@]+@[^@]+|.+)$",
        description="String identifying a Gpsi shall contain either an External Id or an MSISDN.  It shall be formatted as follows -External Identifier= \"extid-'extid', where 'extid'  shall be formatted according to clause 19.7.2 of 3GPP TS 23.003 that describes an  External Identifier. \n",
    ),
]

ExternalGroupId = Annotated[
    str,
    Field(
        ...,
        description='string containing a local identifier followed by "@" and a domain identifier. Both the local identifier and the domain identifier shall be encoded as strings that do not contain any "@" characters. See Clauses 4.6.2 and 4.6.3 of 3GPP TS 23.682 for more information.\n',
    ),
]


class NotificationMethod(Enum):
    """Represents the notification methods that can be subscribed.  \nPossible values are:\n- PERIODIC\n- ONE_TIME\n- ON_EVENT_DETECTION\n"""

    PERIODIC = "PERIODIC"
    ONE_TIME = "ONE_TIME"
    ON_EVENT_DETECTION = "ON_EVENT_DETECTION"


class PartitioningCriteria(Enum):
    """Possible values are:\n- "TAC": Type Allocation Code\n- "SUBPLMN": Subscriber PLMN ID\n- "GEOAREA": Geographical area, i.e. list(s) of TAI(s)\n- "SNSSAI": S-NSSAI\n- "DNN": DNN\n"""

    TAC = "TAC"
    SUBPLMN = "SUBPLMN"
    GEOAREA = "GEOAREA"
    SNSSAI = "SNSSAI"
    DNN = "DNN"


class NotificationFlag(Enum):
    """Possible values are:\n- ACTIVATE: The event notification is activated.\n- DEACTIVATE: The event notification is deactivated and shall be muted. The available\n   event(s) shall be stored.\n- RETRIEVAL: The event notification shall be sent to the NF service consumer(s),\n  after that, is muted again. \n"""

    ACTIVATE = "ACTIVATE"
    DEACTIVATE = "DEACTIVATE"
    RETRIEVAL = "RETRIEVAL"


class BufferedNotificationsAction(Enum):
    """Indicates the required action by the event producer NF on the buffered Notifications.\n"""

    SEND_ALL = "SEND_ALL"
    DISCARD_ALL = "DISCARD_ALL"
    DROP_OLD = "DROP_OLD"


class SubscriptionAction(Enum):
    """Indicates the required action by the event producer NF on the event subscription if an exception occurs while the event is muted.\n"""

    CLOSE = "CLOSE"
    CONTINUE_WITH_MUTING = "CONTINUE_WITH_MUTING"
    CONTINUE_WITHOUT_MUTING = "CONTINUE_WITHOUT_MUTING"


class MutingExceptionInstructions(BaseModel):
    bufferedNotifs: BufferedNotificationsAction | None = None
    subscription: SubscriptionAction | None = None


class MutingNotificationsSettings(BaseModel):
    maxNoOfNotif: int | None = None
    durationBufferedNotif: DurationSec | None = None


class ReportingInformation(BaseModel):
    immRep: bool | None = None
    notifMethod: NotificationMethod | None = None
    maxReportNbr: Uinteger | None = None
    monDur: DateTime | None = None
    repPeriod: DurationSec | None = None
    sampRatio: SamplingRatio | None = None
    partitionCriteria: list[PartitioningCriteria] | None = Field(
        None,
        description="Criteria for partitioning the UEs before applying the sampling ratio.",
        min_length=1,
    )
    grpRepTime: DurationSec | None = None
    notifFlag: NotificationFlag | None = None
    notifFlagInstruct: MutingExceptionInstructions | None = None
    mutingSetting: MutingNotificationsSettings | None = None


Uri = Annotated[
    str,
    Field(
        ..., description="string providing an URI formatted according to IETF RFC 3986."
    ),
]


class NwdafFailureCode(Enum):
    """Represents the failure reason.  \nPossible values are:\n- UNAVAILABLE_DATA: Indicates the requested statistics information for the event is rejected\n  since necessary data to perform the service is unavailable.\n- BOTH_STAT_PRED_NOT_ALLOWED: Indicates the requested analysis information for the event is\n  rejected since the start time is in the past and the end time is in the future, which\n  means the NF service consumer requested both statistics and prediction for the analytics.\n- PREDICTION_NOT_ALLOWED: Indicates that the request for the prediction of the analytics\n  event is not allowed.\n- UNSATISFIED_REQUESTED_ANALYTICS_TIME: Indicates that the requested event is rejected since\n  the analytics information is not ready when the time indicated by the "timeAnaNeeded"\n  attribute (as provided during the creation or modification of subscription) is reached.\n- NO_ROAMING_SUPPORT: Indicates that the request shall be rejected because roaming analytics\n  or data are required and the NWDAF neither supports roaming exchange capabilitiy nor can\n  it forward the request to another NWDAF.\n- OTHER: Indicates the requested analysis information for the event is rejected due to other\n  reasons.\n"""

    UNAVAILABLE_DATA = "UNAVAILABLE_DATA"
    BOTH_STAT_PRED_NOT_ALLOWED = "BOTH_STAT_PRED_NOT_ALLOWED"
    PREDICTION_NOT_ALLOWED = "PREDICTION_NOT_ALLOWED"
    UNSATISFIED_REQUESTED_ANALYTICS_TIME = "UNSATISFIED_REQUESTED_ANALYTICS_TIME"
    NO_ROAMING_SUPPORT = "NO_ROAMING_SUPPORT"
    OTHER = "OTHER"


class EutraLocation(BaseModel):
    tai: Tai
    ignoreTai: bool | None = False
    ecgi: Ecgi
    ignoreEcgi: bool | None = Field(
        False,
        description="This flag when present shall indicate that the Ecgi shall be ignored When present, it shall be set as follows: - true: ecgi shall be ignored. - false (default): ecgi shall not be ignored.\n",
    )
    ageOfLocationInformation: Annotated[
        Optional[int],
        Field(
            ge=0,
            le=32767,
            description='The value represents the elapsed time in minutes since the last network contact of the mobile station.  Value "0" indicates that the location information was obtained after a successful paging procedure for Active Location Retrieval when the UE is in idle mode or after a successful NG-RAN location reporting procedure with the eNB when the UE is in connected mode.  Any other value than "0" indicates that the location information is the last known one.  See 3GPP TS 29.002 clause 17.7.8.\n',
        ),
    ] = None
    ueLocationTimestamp: DateTime | None = None
    geographicalInformation: Annotated[
        Optional[str],
        Field(
            pattern=r"^[0-9A-F]{16}$",
            description="Refer to geographical Information. See 3GPP TS 23.032 clause 7.3.2. Only the description of an ellipsoid point with uncertainty circle is allowed to be used.\n",
        ),
    ] = None
    geodeticInformation: Annotated[
        Optional[str],
        Field(
            pattern=r"^[0-9A-F]{20}$",
            description="Refers to Calling Geodetic Location. See ITU-T Recommendation Q.763 (1999) [24] clause 3.88.2. Only the description of an ellipsoid point with uncertainty circle is allowed to be used.\n",
        ),
    ] = None
    globalNgenbId: GlobalRanNodeId | None = None
    globalENbId: GlobalRanNodeId | None = None


class PlmnIdNid(BaseModel):
    mcc: Mcc
    mnc: Mnc
    nid: Nid | None = None


class NtnTaiInfo(BaseModel):
    plmnId: PlmnIdNid
    tacList: list[Tac] = Field(..., min_length=1)
    derivedTac: Tac | None = None


class NrLocation(BaseModel):
    tai: Tai
    ncgi: Ncgi
    ignoreNcgi: bool | None = False
    ageOfLocationInformation: Annotated[
        Optional[int],
        Field(
            int,
            description='The value represents the elapsed time in minutes since the last network contact of the mobile station. Value "0" indicates that the location information was obtained after a successful paging procedure for Active Location Retrieval when the UE is in idle mode or after a successful  NG-RAN location reporting procedure with the eNB when the UE is in connected mode. Any other value than "0" indicates that the location information is the last known one. See 3GPP TS 29.002 clause 17.7.8.\n',
        ),
    ] = None
    ueLocationTimestamp: DateTime | None = None
    geographicalInformation: Annotated[
        Optional[str],
        Field(
            pattern=r"^[0-9A-F]{16}$",
            description="Refer to geographical Information. See 3GPP TS 23.032 clause 7.3.2. Only the description of an ellipsoid point with uncertainty circle is allowed to be used.\n",
        ),
    ] = None
    geodeticInformation: Annotated[
        Optional[str],
        Field(
            pattern=r"^[0-9A-F]{20}$",
            description="Refers to Calling Geodetic Location. See ITU-T Recommendation Q.763 (1999) [24] clause 3.88.2. Only the description of an ellipsoid point with uncertainty circle is allowed to be used.\n",
        ),
    ] = None
    globalGnbId: GlobalRanNodeId | None = None
    ntnTaiInfo: NtnTaiInfo | None = None


class TransportProtocol(Enum):
    """Possible values are:\n- UDP: User Datagram Protocol.\n- TCP: Transmission Control Protocol. \n"""

    UDP = "UDP"
    TCP = "TCP"


Bytes = Annotated[
    Base64Str,
    Field(..., description="string with format 'bytes' as defined in OpenAPI"),
]


class TnapId(BaseModel):
    ssId: str | None = Field(
        None,
        description="This IE shall be present if the UE is accessing the 5GC via a trusted WLAN access network.When present, it shall contain the SSID of the access point to which the UE is attached, that is received over NGAP,  see IEEE Std 802.11-2012. \n",
    )
    bssId: str | None = Field(
        None,
        description="When present, it shall contain the BSSID of the access point to which the UE is attached, that is received over NGAP, see IEEE Std 802.11-2012. \n",
    )
    civicAddress: Bytes | None = None


class TwapId(BaseModel):
    ssId: str = Field(
        ...,
        description="This IE shall contain the SSID of the access point to which the UE is attached, that is received over NGAP, see IEEE Std 802.11-2012. \n",
    )
    bssId: str | None = Field(
        None,
        description="When present, it shall contain the BSSID of the access point to which the UE is attached, for trusted WLAN access, see IEEE Std 802.11-2012. \n",
    )
    civicAddress: Bytes | None = None


HfcNId = Annotated[
    str,
    Field(
        ...,
        max_length=6,
        description="This IE represents the identifier of the HFC node Id as specified in CableLabs WR-TR-5WWC-ARCH. It is provisioned by the wireline operator as part of wireline operations and may contain up to six characters.\n",
    ),
]


class HfcNodeId(BaseModel):
    hfcNId: HfcNId


class LineType(Enum):
    """Possible values are:\n- DSL: Identifies a DSL line\n- PON: Identifies a PON line\n"""

    DSL = "DSL"
    PON = "PON"


Gci = Annotated[
    str,
    Field(
        ...,
        description="Global Cable Identifier uniquely identifying the connection between the 5G-CRG or FN-CRG to the 5GS. See clause 28.15.4 of 3GPP TS 23.003. This shall be encoded as a string per clause 28.15.4 of 3GPP TS 23.003, and compliant with the syntax specified  in clause 2.2  of IETF RFC 7542 for the username part of a NAI. The GCI value is specified in CableLabs WR-TR-5WWC-ARCH.\n",
    ),
]


class N3gaLocation(BaseModel):
    n3gppTai: Tai | None = None
    n3IwfId: Annotated[
        Optional[str],
        Field(
            pattern=r"^[A-Fa-f0-9]+$",
            description='This IE shall contain the N3IWF identifier received over NGAP and shall be encoded as a  string of hexadecimal characters. Each character in the string shall take a value of "0"  to "9", "a" to "f" or "A" to "F" and shall represent 4 bits. The most significant  character representing the 4 most significant bits of the N3IWF ID shall appear first in  the string, and the character representing the 4 least significant bit of the N3IWF ID  shall appear last in the string. \n',
        ),
    ] = None
    ueIpv4Addr: Ipv4Addr | None = None
    ueIpv6Addr: Ipv6Addr | None = None
    portNumber: Uinteger | None = None
    protocol: TransportProtocol | None = None
    tnapId: TnapId | None = None
    twapId: TwapId | None = None
    hfcNodeId: HfcNodeId | None = None
    gli: Bytes | None = None
    w5gbanLineType: LineType | None = None
    gci: Gci | None = None


class CellGlobalId(BaseModel):
    plmnId: PlmnId
    lac: str = Field(pattern=r"^[A-Fa-f0-9]{4}$")
    cellId: str = Field(pattern=r"^[A-Fa-f0-9]{4}$")


class ServiceAreaId(BaseModel):
    plmnId: PlmnId
    lac: Annotated[
        str, Field(..., pattern=r"^[A-Fa-f0-9]{4}$", description="Location Area Code.")
    ]
    sac: Annotated[
        str, Field(..., pattern=r"^[A-Fa-f0-9]{4}$", description="Service Area Code.")
    ]


class LocationAreaId(BaseModel):
    plmnId: PlmnId
    lac: Annotated[
        str, Field(..., pattern=r"^[A-Fa-f0-9]{4}$", description="Location Area Code.")
    ]


class RoutingAreaId(BaseModel):
    plmnId: PlmnId
    lac: Annotated[
        str, Field(..., pattern=r"^[A-Fa-f0-9]{4}$", description="Location Area Code.")
    ]
    rac: Annotated[
        str, Field(..., pattern=r"^[A-Fa-f0-9]{2}$", description="Routing Area Code")
    ]


class UtraLocation1(BaseModel):
    cgi: CellGlobalId
    sai: ServiceAreaId | None = None
    lai: LocationAreaId | None = None
    rai: RoutingAreaId | None = None
    ageOfLocationInformation: Annotated[
        Optional[int],
        Field(
            ge=0,
            le=32767,
            description='The value represents the elapsed time in minutes since the last network contact of the mobile station.  Value "0" indicates that the location information was obtained after a successful paging procedure for  Active Location Retrieval when the UE is in idle mode\n or after a successful location reporting procedure  the UE is in connected mode. Any\nother value than "0" indicates that the location information is the last known one.  See 3GPP TS 29.002 clause 17.7.8.\n',
        ),
    ] = None
    ueLocationTimestamp: DateTime | None = None
    geographicalInformation: Annotated[
        Optional[str],
        Field(
            pattern=r"^[0-9A-F]{16}$",
            description="Refer to geographical Information.See 3GPP TS 23.032 clause 7.3.2. Only the description of an ellipsoid point with uncertainty circle is allowed to be used.\n",
        ),
    ] = None
    geodeticInformation: Annotated[
        Optional[str],
        Field(
            pattern=r"^[0-9A-F]{20}$",
            description="Refers to Calling Geodetic Location. See ITU-T\xa0Recommendation Q.763 (1999) clause 3.88.2. Only the description of an ellipsoid point with uncertainty circle is allowed to be used.\n",
        ),
    ] = None


class UtraLocation2(BaseModel):
    cgi: CellGlobalId | None = None
    sai: ServiceAreaId
    lai: LocationAreaId | None = None
    rai: RoutingAreaId | None = None
    ageOfLocationInformation: Annotated[
        Optional[int],
        Field(
            ge=0,
            le=32767,
            description='The value represents the elapsed time in minutes since the last network contact of the mobile station.  Value "0" indicates that the location information was obtained after a successful paging procedure for  Active Location Retrieval when the UE is in idle mode\n or after a successful location reporting procedure  the UE is in connected mode. Any\nother value than "0" indicates that the location information is the last known one.  See 3GPP TS 29.002 clause 17.7.8.\n',
        ),
    ] = None
    ueLocationTimestamp: DateTime | None = None
    geographicalInformation: Annotated[
        Optional[str],
        Field(
            pattern=r"^[0-9A-F]{16}$",
            description="Refer to geographical Information.See 3GPP TS 23.032 clause 7.3.2. Only the description of an ellipsoid point with uncertainty circle is allowed to be used.\n",
        ),
    ] = None
    geodeticInformation: Annotated[
        Optional[str],
        Field(
            pattern=r"^[0-9A-F]{20}$",
            description="Refers to Calling Geodetic Location. See ITU-T\xa0Recommendation Q.763 (1999) clause 3.88.2. Only the description of an ellipsoid point with uncertainty circle is allowed to be used.\n",
        ),
    ] = None


class UtraLocation3(BaseModel):
    cgi: CellGlobalId | None = None
    sai: ServiceAreaId | None = None
    lai: LocationAreaId | None = None
    rai: RoutingAreaId
    ageOfLocationInformation: Annotated[
        Optional[int],
        Field(
            ge=0,
            le=32767,
            description='The value represents the elapsed time in minutes since the last network contact of the mobile station.  Value "0" indicates that the location information was obtained after a successful paging procedure for  Active Location Retrieval when the UE is in idle mode\n or after a successful location reporting procedure  the UE is in connected mode. Any\nother value than "0" indicates that the location information is the last known one.  See 3GPP TS 29.002 clause 17.7.8.\n',
        ),
    ] = None
    ueLocationTimestamp: DateTime | None = None
    geographicalInformation: Annotated[
        Optional[str],
        Field(
            pattern=r"^[0-9A-F]{16}$",
            description="Refer to geographical Information.See 3GPP TS 23.032 clause 7.3.2. Only the description of an ellipsoid point with uncertainty circle is allowed to be used.\n",
        ),
    ] = None
    geodeticInformation: Annotated[
        Optional[str],
        Field(
            pattern=r"^[0-9A-F]{20}$",
            description="Refers to Calling Geodetic Location. See ITU-T\xa0Recommendation Q.763 (1999) clause 3.88.2. Only the description of an ellipsoid point with uncertainty circle is allowed to be used.\n",
        ),
    ] = None


class UtraLocation(RootModel[Union[UtraLocation1, UtraLocation2, UtraLocation3]]):
    root: Annotated[
        Union[UtraLocation1, UtraLocation2, UtraLocation3],
        Field(..., description="Exactly one of cgi, sai or lai shall be present."),
    ]


class GeraLocation1(BaseModel):
    locationNumber: str | None = Field(
        None,
        description="Location number within the PLMN. See 3GPP TS 23.003, clause 4.5.",
    )
    cgi: CellGlobalId
    sai: ServiceAreaId | None = None
    lai: LocationAreaId | None = None
    rai: RoutingAreaId | None = None
    vlrNumber: str | None = Field(
        None, description="VLR number. See 3GPP TS 23.003 clause 5.1."
    )
    mscNumber: str | None = Field(
        None, description="MSC number. See 3GPP TS 23.003 clause 5.1."
    )
    ageOfLocationInformation: Annotated[
        Optional[int],
        Field(
            ge=0,
            le=32767,
            description='The value represents the elapsed time in minutes since the last network contact of the mobile station. Value "0" indicates that the location information was obtained after a successful paging procedure for  Active Location Retrieval when the UE is in idle mode or after a successful location reporting procedure the UE is in connected mode. Any other value than "0" indicates that the location information is the last known one. See 3GPP TS 29.002 clause 17.7.8.\n',
        ),
    ] = None
    ueLocationTimestamp: DateTime | None = None
    geographicalInformation: Annotated[
        Optional[str],
        Field(
            pattern=r"^[0-9A-F]{16}$",
            description="Refer to geographical Information.See 3GPP TS 23.032 clause 7.3.2. Only the description of an ellipsoid point with uncertainty circle is allowed to be used.\n",
        ),
    ] = None
    geodeticInformation: Annotated[
        Optional[str],
        Field(
            pattern=r"^[0-9A-F]{20}$",
            description="Refers to Calling Geodetic Location.See ITU-T Recommendation Q.763 (1999) clause 3.88.2.  Only the description of an ellipsoid point with uncertainty circle is allowed to be used.\n",
        ),
    ] = None


class GeraLocation2(BaseModel):
    locationNumber: str | None = Field(
        None,
        description="Location number within the PLMN. See 3GPP TS 23.003, clause 4.5.",
    )
    cgi: CellGlobalId | None = None
    sai: ServiceAreaId
    lai: LocationAreaId | None = None
    rai: RoutingAreaId | None = None
    vlrNumber: str | None = Field(
        None, description="VLR number. See 3GPP TS 23.003 clause 5.1."
    )
    mscNumber: str | None = Field(
        None, description="MSC number. See 3GPP TS 23.003 clause 5.1."
    )
    ageOfLocationInformation: Annotated[
        Optional[int],
        Field(
            ge=0,
            le=32767,
            description='The value represents the elapsed time in minutes since the last network contact of the mobile station. Value "0" indicates that the location information was obtained after a successful paging procedure for  Active Location Retrieval when the UE is in idle mode or after a successful location reporting procedure the UE is in connected mode. Any other value than "0" indicates that the location information is the last known one. See 3GPP TS 29.002 clause 17.7.8.\n',
        ),
    ] = None
    ueLocationTimestamp: DateTime | None = None
    geographicalInformation: Annotated[
        Optional[str],
        Field(
            pattern=r"^[0-9A-F]{16}$",
            description="Refer to geographical Information.See 3GPP TS 23.032 clause 7.3.2. Only the description of an ellipsoid point with uncertainty circle is allowed to be used.\n",
        ),
    ] = None
    geodeticInformation: Annotated[
        Optional[str],
        Field(
            pattern=r"^[0-9A-F]{20}$",
            description="Refers to Calling Geodetic Location.See ITU-T Recommendation Q.763 (1999) clause 3.88.2.  Only the description of an ellipsoid point with uncertainty circle is allowed to be used.\n",
        ),
    ] = None


class GeraLocation3(BaseModel):
    locationNumber: str | None = Field(
        None,
        description="Location number within the PLMN. See 3GPP TS 23.003, clause 4.5.",
    )
    cgi: CellGlobalId | None = None
    sai: ServiceAreaId | None = None
    lai: LocationAreaId
    rai: RoutingAreaId | None = None
    vlrNumber: str | None = Field(
        None, description="VLR number. See 3GPP TS 23.003 clause 5.1."
    )
    mscNumber: str | None = Field(
        None, description="MSC number. See 3GPP TS 23.003 clause 5.1."
    )
    ageOfLocationInformation: Annotated[
        Optional[int],
        Field(
            ge=0,
            le=32767,
            description='The value represents the elapsed time in minutes since the last network contact of the mobile station. Value "0" indicates that the location information was obtained after a successful paging procedure for  Active Location Retrieval when the UE is in idle mode or after a successful location reporting procedure the UE is in connected mode. Any other value than "0" indicates that the location information is the last known one. See 3GPP TS 29.002 clause 17.7.8.\n',
        ),
    ] = None
    ueLocationTimestamp: DateTime | None = None
    geographicalInformation: Annotated[
        Optional[str],
        Field(
            pattern=r"^[0-9A-F]{16}$",
            description="Refer to geographical Information.See 3GPP TS 23.032 clause 7.3.2. Only the description of an ellipsoid point with uncertainty circle is allowed to be used.\n",
        ),
    ] = None
    geodeticInformation: Annotated[
        Optional[str],
        Field(
            pattern=r"^[0-9A-F]{20}$",
            description="Refers to Calling Geodetic Location.See ITU-T Recommendation Q.763 (1999) clause 3.88.2.  Only the description of an ellipsoid point with uncertainty circle is allowed to be used.\n",
        ),
    ] = None


class GeraLocation(RootModel[Union[GeraLocation1, GeraLocation2, GeraLocation3]]):
    root: Annotated[
        Union[GeraLocation1, GeraLocation2, GeraLocation3],
        Field(..., description="Exactly one of cgi, sai or lai shall be present."),
    ]


class UserLocation(BaseModel):
    eutraLocation: EutraLocation | None = None
    nrLocation: NrLocation | None = None
    n3gaLocation: N3gaLocation | None = None
    utraLocation: UtraLocation | None = None
    geraLocation: GeraLocation | None = None


Supi = Annotated[
    str,
    Field(
        ...,
        pattern=r"^(imsi-[0-9]{5,15}|nai-.+|gci-.+|gli-.+|.+)$",
        description='String identifying a Supi that shall contain either an IMSI, a network specific identifier,\na Global Cable Identifier (GCI) or a Global Line Identifier (GLI) as specified in clause \n2.2A of 3GPP TS 23.003. It shall be formatted as follows\n - for an IMSI "imsi-<imsi>", where <imsi> shall be formatted according to clause 2.2\n   of 3GPP TS 23.003 that describes an IMSI.\n - for a network specific identifier "nai-<nai>, where <nai> shall be formatted\n   according to clause 28.7.2 of 3GPP TS 23.003 that describes an NAI.\n - for a GCI "gci-<gci>", where <gci> shall be formatted according to clause 28.15.2\n   of 3GPP TS 23.003.\n - for a GLI "gli-<gli>", where <gli> shall be formatted according to clause 28.16.2 of\n   3GPP TS 23.003.To enable that the value is used as part of an URI, the string shall\n   only contain characters allowed according to the "lower-with-hyphen" naming convention\n   defined in 3GPP TS 29.501.\n',
    ),
]


class GeoDistributionInfo1(BaseModel):
    loc: UserLocation
    supis: list[Supi] = Field(..., min_length=1)
    gpsis: list[Gpsi] | None = Field(None, min_length=1)


class GeoDistributionInfo2(BaseModel):
    loc: UserLocation
    supis: list[Supi] | None = Field(None, min_length=1)
    gpsis: list[Gpsi] = Field(..., min_length=1)


class GeoDistributionInfo(RootModel[Union[GeoDistributionInfo1, GeoDistributionInfo2]]):
    root: Annotated[
        Union[GeoDistributionInfo1, GeoDistributionInfo2],
        Field(..., description="Represents the geographical distribution of the UEs."),
    ]


class DirectionInfo1(BaseModel):
    supi: Supi
    gpsi: Gpsi | None = None
    numOfUe: Uinteger | None = None
    avrSpeed: float | None = None
    ratio: SamplingRatio | None = None
    direction: Direction


class DirectionInfo2(BaseModel):
    supi: Supi | None = None
    gpsi: Gpsi
    numOfUe: Uinteger | None = None
    avrSpeed: float | None = None
    ratio: SamplingRatio | None = None
    direction: Direction


class DirectionInfo(RootModel[Union[DirectionInfo1, DirectionInfo2]]):
    root: Annotated[
        Union[DirectionInfo1, DirectionInfo2],
        Field(..., description="Represents the UE direction information."),
    ]


FlowDescription = Annotated[
    str, Field(..., description="Defines a packet filter of an IP flow.")
]


MacAddr48 = Annotated[
    str,
    Field(
        ...,
        pattern=r"^([0-9a-fA-F]{2})((-[0-9a-fA-F]{2}){5})$",
        description="String identifying a MAC address formatted in the hexadecimal notation according to clause 1.1 and clause 2.1 of RFC 7042.\n",
    ),
]


class FlowDirection(Enum):
    """Indicates the direction of the service data flow.  \nPossible values are:\n- DOWNLINK: The corresponding filter applies for traffic to the UE.\n- UPLINK: The corresponding filter applies for traffic from the UE.\n- BIDIRECTIONAL: The corresponding filter applies for traffic both to and from the UE.\n- UNSPECIFIED: The corresponding filter applies for traffic to the UE (downlink), but has no\nspecific direction declared. The service data flow detection shall apply the filter for\nuplink traffic as if the filter was bidirectional. The PCF shall not use the value\nUNSPECIFIED in filters created by the network in NW-initiated procedures. The PCF shall only\ninclude the value UNSPECIFIED in filters in UE-initiated procedures if the same value is\nreceived from the SMF.\n"""

    DOWNLINK = "DOWNLINK"
    UPLINK = "UPLINK"
    BIDIRECTIONAL = "BIDIRECTIONAL"
    UNSPECIFIED = "UNSPECIFIED"


class EthFlowDescription(BaseModel):
    destMacAddr: MacAddr48 | None = None
    ethType: str
    fDesc: FlowDescription | None = None
    fDir: FlowDirection | None = None
    sourceMacAddr: MacAddr48 | None = None
    vlanTags: list[str] | None = Field(None, max_length=2, min_length=1)
    srcMacAddrEnd: MacAddr48 | None = None
    destMacAddrEnd: MacAddr48 | None = None


class IpEthFlowDescription1(BaseModel):
    ipTrafficFilter: FlowDescription
    ethTrafficFilter: EthFlowDescription | None = None


class IpEthFlowDescription2(BaseModel):
    ipTrafficFilter: FlowDescription | None = None
    ethTrafficFilter: EthFlowDescription


class IpEthFlowDescription(
    RootModel[Union[IpEthFlowDescription1, IpEthFlowDescription2]]
):
    root: Annotated[
        Union[IpEthFlowDescription1, IpEthFlowDescription2],
        Field(
            ...,
            description="Contains the description of an Uplink and/or Downlink Ethernet flow.",
        ),
    ]


class TrafficCharacterization1(BaseModel):
    dnn: Dnn | None = None
    snssai: Snssai | None = None
    appId: ApplicationId | None = None
    fDescs: list[IpEthFlowDescription] | None = Field(None, max_length=2, min_length=1)
    ulVol: Volume
    ulVolVariance: float | None = None
    dlVol: Volume | None = None
    dlVolVariance: float | None = None


class TrafficCharacterization2(BaseModel):
    dnn: Dnn | None = None
    snssai: Snssai | None = None
    appId: ApplicationId | None = None
    fDescs: list[IpEthFlowDescription] | None = Field(None, max_length=2, min_length=1)
    ulVol: Volume | None = None
    ulVolVariance: float | None = None
    dlVol: Volume
    dlVolVariance: float | None = None


class TrafficCharacterization(
    RootModel[Union[TrafficCharacterization1, TrafficCharacterization2]]
):
    root: Annotated[
        Union[TrafficCharacterization1, TrafficCharacterization2],
        Field(..., description="Identifies the detailed traffic characterization."),
    ]


class AppListForUeComm(BaseModel):
    appId: ApplicationId
    startTime: DateTime | None = None
    appDur: DurationSec | None = None
    occurRatio: SamplingRatio | None = None
    spatialValidity: NetworkAreaInfo | None = None


PduSessionId = Annotated[
    int,
    Field(
        ...,
        ge=0,
        le=255,
        description="Unsigned integer identifying a PDU session, within the range 0 to 255, as specified in  clause 11.2.3.1b, bits 1 to 8, of 3GPP TS 24.007. If the PDU Session ID is allocated by the  Core Network for UEs not supporting N1 mode, reserved range 64 to 95 is used. PDU Session ID  within the reserved range is only visible in the Core Network. \n",
    ),
]


class SessInactTimerForUeComm(BaseModel):
    n4SessId: PduSessionId
    sessInactiveTimer: DurationSec


class UeCommunication(BaseModel):
    commDur: DurationSec
    commDurVariance: float | None = None
    perioTime: DurationSec | None = None
    perioTimeVariance: float | None = None
    ts: DateTime | None = None
    tsVariance: float | None = None
    recurringTime: ScheduledCommunicationTime | None = None
    trafChar: TrafficCharacterization
    ratio: SamplingRatio | None = None
    perioCommInd: bool | None = Field(
        None,
        description='This attribute indicates whether the UE communicates periodically or not. Set to "true" to indicate the UE communicates periodically, otherwise set to "false" or omitted.\n',
    )
    confidence: Uinteger | None = None
    anaOfAppList: AppListForUeComm | None = None
    sessInactTimer: SessInactTimerForUeComm | None = None


class AddressList(BaseModel):
    ipv4Addrs: list[Ipv4Addr] | None = Field(None, min_length=1)
    ipv6Addrs: list[Ipv6Addr] | None = Field(None, min_length=1)


class CircumstanceDescription(BaseModel):
    freq: float | None = None
    tm: DateTime | None = None
    locArea: NetworkAreaInfo | None = None
    vol: Volume | None = None


class AdditionalMeasurement(BaseModel):
    unexpLoc: NetworkAreaInfo | None = None
    unexpFlowTeps: list[IpEthFlowDescription] | None = Field(None, min_length=1)
    unexpWakes: list[DateTime] | None = Field(None, min_length=1)
    ddosAttack: AddressList | None = None
    wrgDest: AddressList | None = None
    circums: list[CircumstanceDescription] | None = Field(None, min_length=1)


class CongestionType(Enum):
    """Indicates the congestion analytics type.  \nPossible values are:\n- USER_PLANE: The congestion analytics type is User Plane.\n- CONTROL_PLANE: The congestion analytics type is Control Plane.\n- USER_AND_CONTROL_PLANE: The congestion analytics type is User Plane and Control Plane.\n"""

    USER_PLANE = "USER_PLANE"
    CONTROL_PLANE = "CONTROL_PLANE"
    USER_AND_CONTROL_PLANE = "USER_AND_CONTROL_PLANE"


TosTrafficClass = Annotated[
    str,
    Field(
        ...,
        description="2-octet string, where each octet is encoded in hexadecimal representation. The first octet contains the IPv4 Type-of-Service or the IPv6 Traffic-Class field and the second octet contains the ToS/Traffic Class mask field.\n",
    ),
]


class FlowInfo(BaseModel):
    flowId: int = Field(..., description="Indicates the IP flow identifier.")
    flowDescriptions: list[str] | None = Field(
        None,
        description="Indicates the packet filters of the IP flow. Refer to clause 5.3.8 of 3GPP TS 29.214 for encoding. It shall contain UL and/or DL IP flow description.\n",
        max_length=2,
        min_length=1,
    )
    tosTC: TosTrafficClass | None = None


class TopApplication1(BaseModel):
    appId: ApplicationId
    ipTrafficFilter: FlowInfo | None = None
    ratio: SamplingRatio | None = None


class TopApplication2(BaseModel):
    appId: ApplicationId | None = None
    ipTrafficFilter: FlowInfo
    ratio: SamplingRatio | None = None


class TopApplication(RootModel[Union[TopApplication1, TopApplication2]]):
    root: Annotated[
        Union[TopApplication1, TopApplication2],
        Field(
            ..., description="Top application that contributes the most to the traffic."
        ),
    ]


class DataVolumeTransferTime(BaseModel):
    uplinkVolume: Volume | None = None
    avgTransTimeUl: Uinteger | None = None
    varTransTimeUl: float | None = None
    downlinkVolume: Volume | None = None
    avgTransTimeDl: Uinteger | None = None
    varTransTimeDl: float | None = None


class E2eDataVolTransTimePerUe1(BaseModel):
    supi: Supi | None = None
    gpsi: Gpsi | None = None
    snssai: Snssai | None = None
    accessType: AccessType | None = None
    ratTypes: list[RatType] | None = Field(
        None, description="The RAT types.", min_length=1
    )
    appId: ApplicationId | None = None
    ueLoc: UserLocation
    dnn: Dnn | None = None
    spatialValidity: NetworkAreaInfo | None = None
    validityPeriod: TimeWindow | None = None
    dataVolTransTime: DataVolumeTransferTime | None = None


class E2eDataVolTransTimePerUe2(BaseModel):
    supi: Supi | None = None
    gpsi: Gpsi | None = None
    snssai: Snssai
    accessType: AccessType | None = None
    ratTypes: list[RatType] | None = Field(
        None, description="The RAT types.", min_length=1
    )
    appId: ApplicationId | None = None
    ueLoc: UserLocation | None = None
    dnn: Dnn | None = None
    spatialValidity: NetworkAreaInfo | None = None
    validityPeriod: TimeWindow | None = None
    dataVolTransTime: DataVolumeTransferTime | None = None


class E2eDataVolTransTimePerUe(
    RootModel[Union[E2eDataVolTransTimePerUe1, E2eDataVolTransTimePerUe2]]
):
    root: Annotated[
        Union[E2eDataVolTransTimePerUe1, E2eDataVolTransTimePerUe2],
        Field(..., description="Represents the E2E data volume transfer time per UE."),
    ]


class E2eDataVolTransTimePerTS(BaseModel):
    tsStart: DateTime
    tsDuration: DurationSec
    e2eDataVolTransTimePerUe: list[E2eDataVolTransTimePerUe] = Field(..., min_length=1)


class E2eDataVolTransTimeUeList1(BaseModel):
    highLevel: list[Supi] = Field(..., min_length=1)
    mediumLevel: list[Supi] | None = Field(None, min_length=1)
    lowLevel: list[Supi] | None = Field(None, min_length=1)
    lowRatio: SamplingRatio | None = None
    mediumRatio: SamplingRatio | None = None
    highRatio: SamplingRatio | None = None
    spatialValidity: NetworkAreaInfo | None = None
    validityPeriod: TimeWindow | None = None


class E2eDataVolTransTimeUeList2(BaseModel):
    highLevel: list[Supi] | None = Field(None, min_length=1)
    mediumLevel: list[Supi] = Field(..., min_length=1)
    lowLevel: list[Supi] | None = Field(None, min_length=1)
    lowRatio: SamplingRatio | None = None
    mediumRatio: SamplingRatio | None = None
    highRatio: SamplingRatio | None = None
    spatialValidity: NetworkAreaInfo | None = None
    validityPeriod: TimeWindow | None = None


class E2eDataVolTransTimeUeList3(BaseModel):
    highLevel: list[Supi] | None = Field(None, min_length=1)
    mediumLevel: list[Supi] | None = Field(None, min_length=1)
    lowLevel: list[Supi] = Field(..., min_length=1)
    lowRatio: SamplingRatio | None = None
    mediumRatio: SamplingRatio | None = None
    highRatio: SamplingRatio | None = None
    spatialValidity: NetworkAreaInfo | None = None
    validityPeriod: TimeWindow | None = None


class E2eDataVolTransTimeUeList(
    RootModel[
        Union[
            E2eDataVolTransTimeUeList1,
            E2eDataVolTransTimeUeList2,
            E2eDataVolTransTimeUeList3,
        ]
    ]
):
    root: Annotated[
        Union[
            E2eDataVolTransTimeUeList1,
            E2eDataVolTransTimeUeList2,
            E2eDataVolTransTimeUeList3,
        ],
        Field(
            ...,
            description="Contains the list of UEs classified based on experience level of E2E Data Volume Transfer  Time \n",
        ),
    ]


class E2eDataVolTransTimeInfo(BaseModel):
    e2eDataVolTransTimes: list[E2eDataVolTransTimePerTS] = Field(..., min_length=1)
    e2eDataVolTransTimeUeLists: list[E2eDataVolTransTimeUeList] | None = Field(
        None, min_length=1
    )
    geoDistrInfos: list[GeoDistributionInfo] | None = Field(None, min_length=1)
    confidence: Uinteger | None = None


class ApplicationVolume(BaseModel):
    appId: ApplicationId
    appVolume: Volume


class DispersionCollection(BaseModel):
    ueLoc: UserLocation | None = None
    snssai: Snssai | None = None
    supis: list[Supi] | None = Field(None, min_length=1)
    gpsis: list[Gpsi] | None = Field(None, min_length=1)
    appVolumes: list[ApplicationVolume] | None = Field(None, min_length=1)
    disperAmount: Uinteger | None = None
    disperClass: DispersionClass | None = None
    usageRank: Annotated[
        Optional[int],
        Field(
            ge=1,
            le=3,
            description="Integer where the allowed values correspond to 1, 2, 3 only.",
        ),
    ] = None
    percentileRank: SamplingRatio | None = None
    ueRatio: SamplingRatio | None = None
    confidence: Uinteger | None = None


class DispersionInfo(BaseModel):
    tsStart: DateTime
    tsDuration: DurationSec
    disperCollects: list[DispersionCollection] = Field(..., min_length=1)
    disperType: DispersionType


class UpfInformation(BaseModel):
    upfId: str | None = None
    upfAddr: AddrFqdn | None = None


class PerfData(BaseModel):
    avgTrafficRate: BitRate | None = None
    maxTrafficRate: BitRate | None = None
    minTrafficRate: BitRate | None = None
    aggTrafficRate: BitRate | None = None
    varTrafficRate: float | None = None
    trafRateUeIds: list[Supi] | None = Field(None, min_length=1)
    avePacketDelay: PacketDelBudget | None = None
    maxPacketDelay: PacketDelBudget | None = None
    varPacketDelay: float | None = None
    packDelayUeIds: list[Supi] | None = Field(None, min_length=1)
    avgPacketLossRate: PacketLossRate | None = None
    maxPacketLossRate: PacketLossRate | None = None
    varPacketLossRate: float | None = None
    packLossUeIds: list[Supi] | None = Field(None, min_length=1)
    numOfUe: Uinteger | None = None


class DnPerf(BaseModel):
    appServerInsAddr: AddrFqdn | None = None
    upfInfo: UpfInformation | None = None
    dnai: Dnai | None = None
    perfData: PerfData
    spatialValidCon: NetworkAreaInfo | None = None
    temporalValidCon: TimeWindow | None = None


class DnPerfInfo(BaseModel):
    appId: ApplicationId | None = None
    dnn: Dnn | None = None
    snssai: Snssai | None = None
    dnPerf: list[DnPerf] = Field(..., min_length=1)
    confidence: Uinteger | None = None


class SvcExperience(BaseModel):
    mos: float | None = None
    upperRange: float | None = None
    lowerRange: float | None = None


class ServiceExperienceType(Enum):
    """Represents the type of the service experience analytics.  \nPossible values are:  \n- VOICE: Indicates that the service experience analytics is for voice service.\n- VIDEO: Indicates that the service experience analytics is for video service.\n- OTHER: Indicates that the service experience analytics is for other service.\n"""

    VOICE = "VOICE"
    VIDEO = "VIDEO"
    OTHER = "OTHER"


class SpeedThresholdInfo(BaseModel):
    speedThr: float | None = None
    numOfUe: Uinteger | None = None
    ratio: SamplingRatio | None = None


class MovBehav(BaseModel):
    tsStart: DateTime
    tsDuration: DurationSec
    numOfUe: Uinteger | None = None
    ratio: SamplingRatio | None = None
    avrSpeed: float | None = None
    speedThresdInfos: list[SpeedThresholdInfo] | None = Field(None, min_length=1)
    directionUeInfos: list[DirectionInfo] | None = Field(None, min_length=1)


class MovBehavInfo(BaseModel):
    geoLoc: GeographicalCoordinates | None = None
    movBehavs: list[MovBehav] | None = Field(None, min_length=1)
    confidence: Uinteger | None = None


class TrafficInformation1(BaseModel):
    uplinkRate: BitRate
    downlinkRate: BitRate | None = None
    uplinkVolume: Volume | None = None
    downlinkVolume: Volume | None = None
    totalVolume: Volume | None = None


class TrafficInformation2(BaseModel):
    uplinkRate: BitRate | None = None
    downlinkRate: BitRate
    uplinkVolume: Volume | None = None
    downlinkVolume: Volume | None = None
    totalVolume: Volume | None = None


class TrafficInformation3(BaseModel):
    uplinkRate: BitRate | None = None
    downlinkRate: BitRate | None = None
    uplinkVolume: Volume
    downlinkVolume: Volume | None = None
    totalVolume: Volume | None = None


class TrafficInformation4(BaseModel):
    uplinkRate: BitRate | None = None
    downlinkRate: BitRate | None = None
    uplinkVolume: Volume | None = None
    downlinkVolume: Volume
    totalVolume: Volume | None = None


class TrafficInformation5(BaseModel):
    uplinkRate: BitRate | None = None
    downlinkRate: BitRate | None = None
    uplinkVolume: Volume | None = None
    downlinkVolume: Volume | None = None
    totalVolume: Volume


class TrafficInformation(
    RootModel[
        Union[
            TrafficInformation1,
            TrafficInformation2,
            TrafficInformation3,
            TrafficInformation4,
            TrafficInformation5,
        ]
    ]
):
    root: Annotated[
        Union[
            TrafficInformation1,
            TrafficInformation2,
            TrafficInformation3,
            TrafficInformation4,
            TrafficInformation5,
        ],
        Field(
            ...,
            description="Traffic information including UL/DL data rate and/or Traffic volume.",
        ),
    ]


class WlanPerTsPerformanceInfo1(BaseModel):
    tsStart: DateTime
    tsDuration: DurationSec
    rssi: int
    rtt: Uinteger | None = None
    trafficInfo: TrafficInformation | None = None
    numberOfUes: Uinteger | None = None
    confidence: Uinteger | None = None


class WlanPerTsPerformanceInfo2(BaseModel):
    tsStart: DateTime
    tsDuration: DurationSec
    rssi: int | None = None
    rtt: Uinteger
    trafficInfo: TrafficInformation | None = None
    numberOfUes: Uinteger | None = None
    confidence: Uinteger | None = None


class WlanPerTsPerformanceInfo3(BaseModel):
    tsStart: DateTime
    tsDuration: DurationSec
    rssi: int | None = None
    rtt: Uinteger | None = None
    trafficInfo: TrafficInformation
    numberOfUes: Uinteger | None = None
    confidence: Uinteger | None = None


class WlanPerTsPerformanceInfo4(BaseModel):
    tsStart: DateTime
    tsDuration: DurationSec
    rssi: int | None = None
    rtt: Uinteger | None = None
    trafficInfo: TrafficInformation | None = None
    numberOfUes: Uinteger
    confidence: Uinteger | None = None


class WlanPerTsPerformanceInfo(
    RootModel[
        Union[
            WlanPerTsPerformanceInfo1,
            WlanPerTsPerformanceInfo2,
            WlanPerTsPerformanceInfo3,
            WlanPerTsPerformanceInfo4,
        ]
    ]
):
    root: Annotated[
        Union[
            WlanPerTsPerformanceInfo1,
            WlanPerTsPerformanceInfo2,
            WlanPerTsPerformanceInfo3,
            WlanPerTsPerformanceInfo4,
        ],
        Field(
            ...,
            description="WLAN performance information per Time Slot during the analytics target period.",
        ),
    ]


class WlanPerSsIdPerformanceInfo(BaseModel):
    ssId: str
    wlanPerTsInfos: list[WlanPerTsPerformanceInfo] = Field(..., min_length=1)


class WlanPerUeIdPerformanceInfo1(BaseModel):
    supi: Supi
    gpsi: Gpsi | None = None
    wlanPerTsInfos: list[WlanPerTsPerformanceInfo] = Field(
        ...,
        description="WLAN performance information per Time Slot during the analytics target period.\n",
        min_length=1,
    )


class WlanPerUeIdPerformanceInfo2(BaseModel):
    supi: Supi | None = None
    gpsi: Gpsi
    wlanPerTsInfos: list[WlanPerTsPerformanceInfo] = Field(
        ...,
        description="WLAN performance information per Time Slot during the analytics target period.\n",
        min_length=1,
    )


class WlanPerUeIdPerformanceInfo(
    RootModel[Union[WlanPerUeIdPerformanceInfo1, WlanPerUeIdPerformanceInfo2]]
):
    root: Annotated[
        Union[WlanPerUeIdPerformanceInfo1, WlanPerUeIdPerformanceInfo2],
        Field(..., description="The WLAN performance per UE ID."),
    ]


class TimeToCollisionInfo(BaseModel):
    ttc: DateTime | None = None
    accuracy: Uinteger | None = None
    confidence: Uinteger | None = None


class AnalyticsAccuracyIndication(Enum):
    """Represents the notification methods for the subscribed events.  \nPossible values are:\n- MEET: Indicates meet the analytics accuracy requirement.\n- NOT_MEET: Indicates not meet the analytics accuracy requirement.\n"""

    MEET = "MEET"
    NOT_MEET = "NOT_MEET"


class AccuracyInfo(BaseModel):
    accuracyVal: Uinteger
    accuSampleNbr: Uinteger | None = None
    anaAccuInd: AnalyticsAccuracyIndication | None = None


LoadLevelInformation = Annotated[
    int,
    Field(
        ...,
        description="Load level information of the network slice and the optionally associated network slice instance.\n",
    ),
]


class ResourceUsage(BaseModel):
    cpuUsage: Uinteger | None = None
    memoryUsage: Uinteger | None = None
    storageUsage: Uinteger | None = None


class NumberAverage(BaseModel):
    number: float
    variance: float
    skewness: float | None = None


class NsiLoadLevelInfo(BaseModel):
    loadLevelInformation: LoadLevelInformation
    snssai: Snssai
    nsiId: NsiId | None = None
    resUsage: ResourceUsage | None = None
    numOfExceedLoadLevelThr: Uinteger | None = None
    exceedLoadLevelThrInd: bool | None = Field(
        None,
        description='Indicates whether the Load Level Threshold is met or exceeded by the statistics value. Set to "true" if the Load Level Threshold is met or exceeded, otherwise set to "false". Shall be present if one of the element in the "listOfAnaSubsets" attribute was set to EXCEED_LOAD_LEVEL_THR_IND.\n',
    )
    networkArea: NetworkAreaInfo | None = None
    timePeriod: TimeWindow | None = None
    resUsgThrCrossTimePeriod: list[TimeWindow] | None = Field(
        None,
        description='Each element indicates the time elapsed between times each threshold is met or exceeded or crossed. The start time and end time are the exact time stamps of the resource usage threshold is reached or exceeded. May be present if the "listOfAnaSubsets" attribute is provided and the maximum number of instances shall not exceed the value provided in the "numOfExceedLoadLevelThr" attribute.\n',
        min_length=1,
    )
    numOfUes: NumberAverage | None = None
    numOfPduSess: NumberAverage | None = None
    confidence: Uinteger | None = None


Link = Annotated[
    str,
    Field(
        ...,
        description="string formatted according to IETF RFC 3986 identifying a referenced resource.",
    ),
]


class WebsockNotifConfig(BaseModel):
    websocketUri: Link | None = None
    requestWebsocketUri: bool | None = Field(
        None,
        description="Set by the SCS/AS to indicate that the Websocket delivery is requested.",
    )


class InvalidParam(BaseModel):
    param: str = Field(
        ..., description="Attribute's name encoded as a JSON Pointer, or header's name."
    )
    reason: str | None = Field(
        None, description='A human-readable reason, e.g. "must be a positive integer".'
    )


class ProblemDetails(BaseModel):
    type: Uri | None = None
    title: str | None = Field(
        None,
        description="A short, human-readable summary of the problem type. It should not change from occurrence to occurrence of the problem. \n",
    )
    status: int | None = Field(
        None, description="The HTTP status code for this occurrence of the problem."
    )
    detail: str | None = Field(
        None,
        description="A human-readable explanation specific to this occurrence of the problem.",
    )
    instance: Uri | None = None
    cause: str | None = Field(
        None,
        description="A machine-readable application error cause specific to this occurrence of the problem. This IE should be present and provide application-related error information, if available.\n",
    )
    invalidParams: list[InvalidParam] | None = Field(
        None,
        description="Description of invalid parameters, for a request rejected due to invalid parameters.\n",
        min_length=1,
    )
    supportedFeatures: SupportedFeatures | None = None


class TermCause(Enum):
    """Represents the cause for the analytics subscription termination request.  \nPossible values are:  \n  - USER_CONSENT_REVOKED: The user consent has been revoked.\n  - NWDAF_OVERLOAD: The NWDAF is overloaded.\n  - UE_LEFT_AREA: The UE has moved out of the NWDAF serving area.\n"""

    USER_CONSENT_REVOKED = "USER_CONSENT_REVOKED"
    NWDAF_OVERLOAD = "NWDAF_OVERLOAD"
    UE_LEFT_AREA = "UE_LEFT_AREA"


class UserDataCongestReq(BaseModel):
    orderCriterion: UserDataConOrderCrit | None = None
    orderDirection: MatchingDirection | None = None


class Error(Enum):
    invalid_request = "invalid_request"
    invalid_client = "invalid_client"
    invalid_grant = "invalid_grant"
    unauthorized_client = "unauthorized_client"
    unsupported_grant_type = "unsupported_grant_type"
    invalid_scope = "invalid_scope"


class AccessTokenErr(BaseModel):
    error: Error
    error_description: str | None = None
    error_uri: str | None = None


class NFType(Enum):
    """NF types known to NRF"""

    NRF = "NRF"
    UDM = "UDM"
    AMF = "AMF"
    SMF = "SMF"
    AUSF = "AUSF"
    NEF = "NEF"
    PCF = "PCF"
    SMSF = "SMSF"
    NSSF = "NSSF"
    UDR = "UDR"
    LMF = "LMF"
    GMLC = "GMLC"
    field_5G_EIR = "5G_EIR"
    SEPP = "SEPP"
    UPF = "UPF"
    N3IWF = "N3IWF"
    AF = "AF"
    UDSF = "UDSF"
    BSF = "BSF"
    CHF = "CHF"
    NWDAF = "NWDAF"
    PCSCF = "PCSCF"
    CBCF = "CBCF"
    HSS = "HSS"
    UCMF = "UCMF"
    SOR_AF = "SOR_AF"
    SPAF = "SPAF"
    MME = "MME"
    SCSAS = "SCSAS"
    SCEF = "SCEF"
    SCP = "SCP"
    NSSAAF = "NSSAAF"
    ICSCF = "ICSCF"
    SCSCF = "SCSCF"
    DRA = "DRA"
    IMS_AS = "IMS_AS"
    AANF = "AANF"
    field_5G_DDNMF = "5G_DDNMF"
    NSACF = "NSACF"
    MFAF = "MFAF"
    EASDF = "EASDF"
    DCCF = "DCCF"
    MB_SMF = "MB_SMF"
    TSCTSF = "TSCTSF"
    ADRF = "ADRF"
    GBA_BSF = "GBA_BSF"
    CEF = "CEF"
    MB_UPF = "MB_UPF"
    NSWOF = "NSWOF"
    PKMF = "PKMF"
    MNPF = "MNPF"
    SMS_GMSC = "SMS_GMSC"
    SMS_IWMSC = "SMS_IWMSC"
    MBSF = "MBSF"
    MBSTF = "MBSTF"
    PANF = "PANF"
    IP_SM_GW = "IP_SM_GW"
    SMS_ROUTER = "SMS_ROUTER"
    DCSF = "DCSF"
    MRF = "MRF"
    MRFP = "MRFP"
    MF = "MF"
    SLPKMF = "SLPKMF"
    RH = "RH"


Fqdn = Annotated[
    str,
    Field(
        ...,
        pattern=r"^([0-9A-Za-z]([-0-9A-Za-z]{0,61}[0-9A-Za-z])?\.)+[A-Za-z]{2,63}\.?$",
        min_length=4,
        max_length=253,
        description="Fully Qualified Domain Name",
    ),
]

NfSetId = Annotated[
    str,
    Field(
        ...,
        description='NF Set Identifier (see clause 28.12 of 3GPP TS 23.003), formatted as the following string "set<Set ID>.<nftype>set.5gc.mnc<MNC>.mcc<MCC>", or  "set<SetID>.<NFType>set.5gc.nid<NID>.mnc<MNC>.mcc<MCC>" with  <MCC> encoded as defined in clause 5.4.2 ("Mcc" data type definition)  <MNC> encoding the Mobile Network Code part of the PLMN, comprising 3 digits. \n  If there are only 2 significant digits in the MNC, one "0" digit shall be inserted \n  at the left side to fill the 3 digits coding of MNC.  Pattern: \'^[0-9]{3}$\'\n<NFType> encoded as a value defined in Table 6.1.6.3.3-1 of 3GPP TS 29.510 but \n  with lower case characters <Set ID> encoded as a string of characters consisting of \n  alphabetic characters (A-Z and a-z), digits (0-9) and/or the hyphen (-) and that \n  shall end with either an alphabetic character or a digit. \n',
    ),
]

NfServiceSetId = Annotated[
    str,
    Field(
        ...,
        description='NF Service Set Identifier (see clause 28.12 of 3GPP TS 23.003) formatted as the following  string "set<Set ID>.sn<Service Name>.nfi<NF Instance ID>.5gc.mnc<MNC>.mcc<MCC>", or  "set<SetID>.sn<ServiceName>.nfi<NFInstanceID>.5gc.nid<NID>.mnc<MNC>.mcc<MCC>" with  <MCC> encoded as defined in clause 5.4.2 ("Mcc" data type definition)   <MNC> encoding the Mobile Network Code part of the PLMN, comprising 3 digits. \n  If there are only 2 significant digits in the MNC, one "0" digit shall be inserted \n  at the left side to fill the 3 digits coding of MNC.  Pattern: \'^[0-9]{3}$\'\n<NID> encoded as defined in clause\xa05.4.2 ("Nid" data type definition)  <NFInstanceId> encoded as defined in clause 5.3.2  <ServiceName> encoded as defined in 3GPP TS 29.510  <Set ID> encoded as a string of characters consisting of alphabetic \n  characters (A-Z and a-z), digits (0-9) and/or the hyphen (-) and that shall end \n  with either an alphabetic character or a digit.\n',
    ),
]

VendorId = Annotated[
    str,
    Field(
        ...,
        pattern=r"^[0-9]{6}$",
        description="Vendor ID of the NF Service instance (Private Enterprise Number assigned by IANA)",
    ),
]


class MlModelInterInd(BaseModel):
    analyticsId: NwdafEvent
    vendorList: list[VendorId] = Field(..., min_length=1)


class GrantType(Enum):
    client_credentials = "client_credentials"


class AccessTokenReq(BaseModel):
    grant_type: GrantType
    nfInstanceId: NfInstanceId
    nfType: NFType | None = None
    targetNfType: NFType | None = None
    scope: str = Field(pattern=r"^([a-zA-Z0-9_:-]+)( [a-zA-Z0-9_:-]+)*$")
    targetNfInstanceId: NfInstanceId | None = None
    requesterPlmn: PlmnId | None = None
    requesterPlmnList: list[PlmnId] | None = Field(None, min_length=2)
    requesterSnssaiList: list[Snssai] | None = Field(None, min_length=1)
    requesterFqdn: Fqdn | None = None
    requesterSnpnList: list[PlmnIdNid] | None = Field(None, min_length=1)
    targetPlmn: PlmnId | None = None
    targetSnpn: PlmnIdNid | None = None
    targetSnssaiList: list[Snssai] | None = Field(None, min_length=1)
    targetNsiList: list[str] | None = Field(None, min_length=1)
    targetNfSetId: NfSetId | None = None
    targetNfServiceSetId: NfServiceSetId | None = None
    hnrfAccessTokenUri: Uri | None = None
    sourceNfInstanceId: NfInstanceId | None = None
    vendorId: VendorId | None = None
    analyticsIds: list[NwdafEvent] | None = Field(None, min_length=1)
    requesterInterIndList: list[MlModelInterInd] | None = Field(None, min_length=1)
    sourceVendorId: VendorId | None = None


class NoProfileMatchReason(Enum):
    """No Profile Match Reason"""

    REQUESTER_PLMN_NOT_ALLOWED = "REQUESTER_PLMN_NOT_ALLOWED"
    TARGET_NF_SUSPENDED = "TARGET_NF_SUSPENDED"
    TARGET_NF_UNDISCOVERABLE = "TARGET_NF_UNDISCOVERABLE"
    QUERY_PARAMS_COMBINATION_NO_MATCH = "QUERY_PARAMS_COMBINATION_NO_MATCH"
    TARGET_NF_TYPE_NOT_SUPPORTED = "TARGET_NF_TYPE_NOT_SUPPORTED"
    UNSPECIFIED = "UNSPECIFIED"


class QueryParameter(BaseModel):
    name: str
    value: str


class QueryParamCombination(BaseModel):
    queryParams: list[QueryParameter] = Field(..., min_length=1)


class NoProfileMatchInfo(BaseModel):
    reason: NoProfileMatchReason
    queryParamCombinationList: list[QueryParamCombination] | None = Field(
        None, min_length=1
    )


class AdditionInfoAnalyticsInfoRequest(BaseModel):
    rvWaitTime: DurationSec | None = None


class ProblemDetailsAnalyticsInfoRequest(
    ProblemDetails, AdditionInfoAnalyticsInfoRequest
):
    pass


class TargetUeId(BaseModel):
    anyUeInd: bool | None = None
    gpsi: Gpsi | None = None
    exterGroupId: ExternalGroupId | None = None


class AbnormalExposure(BaseModel):
    gpsis: list[Gpsi] | None = Field(None, min_length=1)
    appId: ApplicationId | None = None
    dnn: Dnn | None = None
    snssai: Snssai | None = None
    excep: Exception
    ratio: SamplingRatio | None = None
    confidence: Uinteger | None = None
    addtMeasInfo: AdditionalMeasurement | None = None


class CongestionAnalytics(BaseModel):
    cngType: CongestionType
    tmWdw: TimeWindow
    nsi: ThresholdLevel
    confidence: Uinteger | None = None
    topAppListUl: list[TopApplication] | None = Field(None, min_length=1)
    topAppListDl: list[TopApplication] | None = Field(None, min_length=1)


class AnalyticsFailureEventInfo(BaseModel):
    event: AnalyticsEvent
    failureCode: AnalyticsFailureCode


class GADShape(BaseModel):
    shape: SupportedGADShapes


class PointUncertaintyCircle(GADShape):
    point: GeographicalCoordinates
    uncertainty: Uncertainty


class PointUncertaintyEllipse(GADShape):
    point: GeographicalCoordinates
    uncertaintyEllipse: UncertaintyEllipse
    confidence: Confidence


class Polygon(GADShape):
    pointList: PointList


class PointAltitude(GADShape):
    point: GeographicalCoordinates
    altitude: Altitude


class PointAltitudeUncertainty(GADShape):
    point: GeographicalCoordinates
    altitude: Altitude
    uncertaintyEllipse: UncertaintyEllipse
    uncertaintyAltitude: Uncertainty
    confidence: Confidence
    vConfidence: Confidence | None = None


class EllipsoidArc(GADShape):
    point: GeographicalCoordinates
    innerRadius: InnerRadius
    uncertaintyRadius: Uncertainty
    offsetAngle: Angle
    includedAngle: Angle
    confidence: Confidence


class Point(GADShape):
    point: GeographicalCoordinates


class GeographicArea(
    RootModel[
        Union[
            Point,
            PointUncertaintyCircle,
            PointUncertaintyEllipse,
            Polygon,
            PointAltitude,
            PointAltitudeUncertainty,
            EllipsoidArc,
        ]
    ]
):
    root: Annotated[
        Union[
            Point,
            PointUncertaintyCircle,
            PointUncertaintyEllipse,
            Polygon,
            PointAltitude,
            PointAltitudeUncertainty,
            EllipsoidArc,
        ],
        Field(..., description="Geographic area specified by different shape."),
    ]


class LocalOrigin(BaseModel):
    coordinateId: str
    point: GeographicalCoordinates | None = None
    area: GeographicArea | None = None
    horizAxesOrientation: HorizAxesOrientation | None = None


class Local2dPointUncertaintyEllipse(GADShape):
    localOrigin: LocalOrigin
    point: RelativeCartesianLocation
    uncertaintyEllipse: UncertaintyEllipse
    confidence: Confidence


class Local3dPointUncertaintyEllipsoid(GADShape):
    localOrigin: LocalOrigin
    point: RelativeCartesianLocation
    uncertaintyEllipsoid: UncertaintyEllipsoid
    confidence: Confidence
    vConfidence: Confidence | None = None


class LocationArea5G(BaseModel):
    geographicAreas: list[GeographicArea] | None = Field(
        None,
        description="Identifies a list of geographic area of the user where the UE is located.",
        min_length=0,
    )
    civicAddresses: list[CivicAddress] | None = Field(
        None,
        description="Identifies a list of civic addresses of the user where the UE is located.",
        min_length=0,
    )
    nwAreaInfo: NetworkAreaInfo | None = None


class GeographicalArea(BaseModel):
    civicAddress: CivicAddress | None = None
    shapes: GeographicArea | None = None


class LocationArea(BaseModel):
    geographicAreas: list[GeographicArea] | None = Field(
        None,
        description="Identifies a list of geographic area of the user where the UE is located.",
        min_length=0,
    )
    civicAddresses: list[CivicAddress] | None = Field(
        None,
        description="Identifies a list of civic addresses of the user where the UE is located.",
        min_length=0,
    )
    nwAreaInfo: NetworkAreaInfo | None = None
    umtTime: UmtTime | None = None


class ExpectedUeBehaviourData(BaseModel):
    stationaryIndication: StationaryIndication | None = None
    communicationDurationTime: DurationSec | None = None
    periodicTime: DurationSec | None = None
    scheduledCommunicationTime: ScheduledCommunicationTime | None = None
    scheduledCommunicationType: ScheduledCommunicationType | None = None
    expectedUmts: list[LocationArea] | None = Field(
        None,
        description="Identifies the UE's expected geographical movement. The attribute is only applicable in 5G.\n",
        min_length=1,
    )
    trafficProfile: TrafficProfile | None = None
    batteryIndication: BatteryIndication | None = None
    validityTime: DateTime | None = None
    confidenceLevel: Annotated[
        Optional[str], Field(pattern=r"^[0]\.[0-9]{2}$|^1\.00$")
    ] = None
    accuracyLevel: Annotated[
        Optional[str], Field(pattern=r"^[0]\.[0-9]{2}$|^1\.00$")
    ] = None


class LocationInfo(BaseModel):
    loc: UserLocation
    geoLoc: GeographicalArea | None = None
    ratio: SamplingRatio | None = None
    confidence: Uinteger | None = None
    geoDistrInfos: list[GeoDistributionInfo] | None = Field(None, min_length=1)
    distThreshold: Uinteger | None = None


class ServiceExperienceInfo(BaseModel):
    svcExprc: SvcExperience
    svcExprcVariance: float | None = None
    supis: list[Supi] | None = Field(None, min_length=1)
    snssai: Snssai | None = None
    appId: ApplicationId | None = None
    srvExpcType: ServiceExperienceType | None = None
    ueLocs: list[LocationInfo] | None = Field(None, min_length=1)
    upfInfo: UpfInformation | None = None
    dnai: Dnai | None = None
    appServerInst: AddrFqdn | None = None
    confidence: Uinteger | None = None
    dnn: Dnn | None = None
    networkArea: NetworkAreaInfo | None = None
    nsiId: NsiId | None = None
    ratio: SamplingRatio | None = None
    ratFreq: RatFreqInformation | None = None
    pduSesInfo: PduSessionInfo | None = None


class TimestampedLocation(BaseModel):
    ts: DateTime
    locInfo: list[LocationInfo]


class UeTrajectory1(BaseModel):
    supi: Supi
    gpsi: Gpsi | None = None
    timestampedLocs: list[TimestampedLocation] = Field(..., min_length=1)


class UeTrajectory2(BaseModel):
    supi: Supi | None = None
    gpsi: Gpsi
    timestampedLocs: list[TimestampedLocation] = Field(..., min_length=1)


class UeTrajectory(RootModel[Union[UeTrajectory1, UeTrajectory2]]):
    root: Annotated[
        Union[UeTrajectory1, UeTrajectory2],
        Field(..., description="Represents timestamped UE positions."),
    ]


class UeProximity(BaseModel):
    ueDistance: int | None = None
    ueVelocity: VelocityEstimate | None = None
    avrSpeed: float | None = None
    locOrientation: LocationOrientation | None = None
    ueTrajectories: list[UeTrajectory] | None = Field(None, min_length=1)
    ratio: SamplingRatio | None = None


class RelProxInfo(BaseModel):
    tsStart: DateTime
    tsDuration: DurationSec
    supis: list[Supi] | None = Field(None, min_length=1)
    gpsis: list[Gpsi] | None = Field(None, min_length=1)
    ueProximities: list[UeProximity] = Field(..., min_length=1)
    ttcInfo: TimeToCollisionInfo | None = None


class AnalyticsEventFilterSubsc(BaseModel):
    nwPerfReqs: list[NetworkPerfRequirement] | None = Field(None, min_length=1)
    locArea: LocationArea5G | None = None
    fineGranAreas: list[GeographicalArea] | None = Field(
        None,
        description="Indicates the fine granularity areas to which the subscription applies.",
        min_length=1,
    )
    temporalGranSize: DurationSec | None = None
    spatialGranSizeTa: Uinteger | None = None
    spatialGranSizeCell: Uinteger | None = None
    appIds: list[ApplicationId] | None = Field(None, min_length=1)
    dnn: Dnn | None = None
    dnns: list[Dnn] | None = Field(None, min_length=1)
    dnais: list[Dnai] | None = Field(None, min_length=1)
    dataVlTrnsTmRqs: list[E2eDataVolTransTimeReq] | None = Field(None, min_length=1)
    excepRequs: list[Exception] | None = Field(None, min_length=1)
    exptAnaType: ExpectedAnalyticsType | None = None
    exptUeBehav: ExpectedUeBehaviourData | None = None
    matchingDir: MatchingDirection | None = None
    reptThlds: list[ThresholdLevel] | None = Field(None, min_length=1)
    snssai: Snssai | None = None
    snssais: list[Snssai] | None = Field(None, min_length=1)
    nsiIdInfos: list[NsiIdInfo] | None = Field(None, min_length=1)
    qosReq: QosRequirement | None = None
    qosFlowRetThds: list[RetainabilityThreshold] | None = Field(None, min_length=1)
    ranUeThrouThds: list[BitRate] | None = Field(None, min_length=1)
    disperReqs: list[DispersionRequirement] | None = Field(None, min_length=1)
    listOfAnaSubsets: list[AnalyticsSubset] | None = Field(None, min_length=1)
    dnPerfReqs: list[DnPerformanceReq] | None = Field(None, min_length=1)
    bwRequs: list[BwRequirement] | None = Field(None, min_length=1)
    ratFreqs: list[RatFreqInformation] | None = Field(None, min_length=1)
    appServerAddrs: list[AddrFqdn] | None = Field(None, min_length=1)
    wlanReqs: list[WlanPerformanceReq] | None = Field(None, min_length=1)
    extraReportReq: EventReportingRequirement | None = None
    maxNumOfTopAppUl: Uinteger | None = None
    maxNumOfTopAppDl: Uinteger | None = None
    visitedLocAreas: list[LocationArea5G] | None = Field(None, min_length=1)
    pduSesInfos: list[PduSessionInfo] | None = Field(None, min_length=1)
    ueCommReqs: list[UeCommReq] | None = Field(None, min_length=1)
    userDataConOrderCri: UserDataConOrderCrit | None = None
    locGranularity: LocInfoGranularity | None = None
    locOrientation: LocationOrientation | None = None
    ueMobilityReqs: list[UeMobilityReq] | None = Field(None, min_length=1)
    movBehavReqs: list[MovBehavReq] | None = Field(None, min_length=1)
    relProxReqs: list[RelProxReq] | None = Field(None, min_length=1)
    useCaseCxt: str | None = Field(
        None,
        description="Indicates the context of usage of the analytics. The value and format of this parameter are not standardized.\n",
    )
    pauseFlg: bool | None = Field(
        None,
        description='Pause analytics consumption flag. Set to "true" to indicate the NWDAF to stop sending the notifications of analytics. Default value is "false" if omitted.\n',
    )
    resumeFlg: bool | None = Field(
        None,
        description='Resume analytics consumption flag. Set to "true" to indicate the NWDAF to resume sending the notifications of analytics. Default value is "false" if omitted.\n',
    )
    accuReq: AccuracyReq | None = None
    feedback: AnalyticsFeedbackInfo | None = None


class UeLocationInfo(BaseModel):
    loc: LocationArea5G
    geoLoc: GeographicalArea | None = None
    ratio: SamplingRatio | None = None
    confidence: Uinteger | None = None
    geoDistrInfos: list[GeoDistributionInfo] | None = Field(None, min_length=1)


class AnalyticsEventFilter(BaseModel):
    locArea: LocationArea5G | None = None
    fineGranAreas: list[GeographicalArea] | None = Field(
        None,
        description="Indicates the fine granularity areas to which the request applies.",
        min_length=1,
    )
    temporalGranSize: DurationSec | None = None
    spatialGranSizeTa: Uinteger | None = None
    spatialGranSizeCell: Uinteger | None = None
    dnn: Dnn | None = None
    dnns: list[Dnn] | None = Field(None, min_length=1)
    dnais: list[Dnai] | None = Field(None, min_length=1)
    nwPerfTypes: list[NetworkPerfType] | None = Field(None, min_length=1)
    appIds: list[ApplicationId] | None = Field(None, min_length=1)
    excepIds: list[ExceptionId] | None = Field(None, min_length=1)
    exptAnaType: ExpectedAnalyticsType | None = None
    exptUeBehav: ExpectedUeBehaviourData | None = None
    snssai: Snssai | None = None
    snssais: list[Snssai] | None = Field(None, min_length=1)
    nsiIdInfos: list[NsiIdInfo] | None = Field(None, min_length=1)
    qosReq: QosRequirement | None = None
    listOfAnaSubsets: list[AnalyticsSubset] | None = Field(None, min_length=1)
    dnPerfReqs: list[DnPerformanceReq] | None = Field(None, min_length=1)
    dataVlTrnsTmReqs: list[E2eDataVolTransTimeReq] | None = Field(None, min_length=1)
    bwRequs: list[BwRequirement] | None = Field(None, min_length=1)
    ratFreqs: list[RatFreqInformation] | None = Field(None, min_length=1)
    appServerAddrs: list[AddrFqdn] | None = Field(None, min_length=1)
    wlanReqs: list[WlanPerformanceReq] | None = Field(None, min_length=1)
    disperReqs: list[DispersionRequirement] | None = Field(None, min_length=1)
    maxNumOfTopAppUl: Uinteger | None = None
    maxNumOfTopAppDl: Uinteger | None = None
    visitedLocAreas: list[LocationArea5G] | None = Field(None, min_length=1)
    pduSesInfos: list[PduSessionInfo] | None = Field(None, min_length=1)
    ueCommReqs: list[UeCommReq] | None = Field(None, min_length=1)
    userDataConReq: UserDataCongestReq | None = None
    locGranularity: LocInfoGranularity | None = None
    locOrientation: LocationOrientation | None = None
    ueMobilityReqs: list[UeMobilityReq] | None = Field(None, min_length=1)
    movBehavReqs: list[MovBehavReq] | None = Field(None, min_length=1)
    useCaseCxt: str | None = Field(
        None,
        description="Indicates the context of usage of the analytics. The value and format of this parameter are not standardized.\n",
    )
    accuReq: AccuracyReq | None = None
    relProxReqs: list[RelProxReq] | None = Field(None, min_length=1)


class NetworkPerfExposure(BaseModel):
    locArea: LocationArea5G
    anaPeriod: TimeWindow | None = None
    nwPerfType: NetworkPerfType
    relativeRatio: SamplingRatio | None = None
    absoluteNum: Uinteger | None = None
    rscUsgReq: ResourceUsageRequirement | None = None
    confidence: Uinteger | None = None


class CongestInfo(BaseModel):
    locArea: LocationArea5G
    cngAnas: list[CongestionAnalytics] = Field(..., min_length=1)


class QosSustainabilityExposure(BaseModel):
    locArea: LocationArea5G
    fineAreaInfos: list[GeographicalArea] | None = Field(
        None,
        description="This attribute contains the geographical locations in a fine granularity.",
        min_length=1,
    )
    startTs: DateTime
    endTs: DateTime
    qosFlowRetThd: RetainabilityThreshold | None = None
    ranUeThrouThd: BitRate | None = None
    snssai: Snssai | None = None
    confidence: Uinteger | None = None


class WlanPerformInfo(BaseModel):
    locArea: LocationArea5G | None = None
    wlanPerSsidInfos: list[WlanPerSsIdPerformanceInfo] = Field(..., min_length=1)
    wlanPerUeIdInfos: list[WlanPerUeIdPerformanceInfo] | None = Field(
        None,
        description="WLAN performance information for UE Id(s) of WLAN access points deployed in the Area of Interest.\n",
        min_length=1,
    )


class AnalyticsEventSubsc(BaseModel):
    analyEvent: AnalyticsEvent
    analyEventFilter: AnalyticsEventFilterSubsc | None = None
    tgtUe: TargetUeId | None = None


class UeMobilityExposure(BaseModel):
    ts: DateTime | None = None
    recurringTime: ScheduledCommunicationTime | None = None
    duration: DurationSec
    durationVariance: float | None = None
    locInfo: list[UeLocationInfo] = Field(..., min_length=1)
    directionInfos: list[DirectionInfo] | None = Field(None, min_length=1)


class AnalyticsRequest(BaseModel):
    analyEvent: AnalyticsEvent
    analyEventFilter: AnalyticsEventFilter | None = None
    analyRep: EventReportingRequirement | None = None
    tgtUe: TargetUeId | None = None
    suppFeat: SupportedFeatures


class AnalyticsData(BaseModel):
    start: DateTime | None = None
    expiry: DateTime | None = None
    timeStampGen: DateTime | None = None
    ueMobilityInfos: list[UeMobilityExposure] | None = Field(None, min_length=1)
    ueCommInfos: list[UeCommunication] | None = Field(None, min_length=1)
    nwPerfInfos: list[NetworkPerfExposure] | None = Field(None, min_length=1)
    abnormalInfos: list[AbnormalExposure] | None = Field(None, min_length=1)
    congestInfos: list[CongestInfo] | None = Field(None, min_length=1)
    dataVlTrnsTmInfos: list[E2eDataVolTransTimeInfo] | None = Field(None, min_length=1)
    qosSustainInfos: list[QosSustainabilityExposure] | None = Field(None, min_length=1)
    disperInfos: list[DispersionInfo] | None = Field(None, min_length=1)
    dnPerfInfos: list[DnPerfInfo] | None = Field(None, min_length=1)
    svcExps: list[ServiceExperienceInfo] | None = Field(None, min_length=1)
    movBehavInfos: list[MovBehavInfo] | None = Field(None, min_length=1)
    wlanInfos: list[WlanPerformInfo] | None = Field(None, min_length=1)
    accuInfo: AccuracyInfo | None = None
    cancelAccuInd: bool | None = Field(
        None,
        description='Indicates cancelled request of the analytics accuracy information. Set to "true" indicates the NWDAF cancelled request of analytics accuracy information as the NWDAF does not support the accuracy checking capability. Otherwise set to "false". Default value is "false" if omitted.\n',
    )
    relProxInfos: list[RelProxInfo] | None = Field(None, min_length=1)
    suppFeat: SupportedFeatures


class AnalyticsEventNotif(BaseModel):
    analyEvent: AnalyticsEvent
    expiry: DateTime | None = None
    timeStamp: DateTime
    failNotifyCode: NwdafFailureCode | None = None
    rvWaitTime: DurationSec | None = None
    ueMobilityInfos: list[UeMobilityExposure] | None = Field(None, min_length=1)
    ueCommInfos: list[UeCommunication] | None = Field(None, min_length=1)
    abnormalInfos: list[AbnormalExposure] | None = Field(None, min_length=1)
    congestInfos: list[CongestInfo] | None = Field(None, min_length=1)
    dataVlTrnsTmIfs: list[E2eDataVolTransTimeInfo] | None = Field(None, min_length=1)
    nwPerfInfos: list[NetworkPerfExposure] | None = Field(None, min_length=1)
    qosSustainInfos: list[QosSustainabilityExposure] | None = Field(None, min_length=1)
    disperInfos: list[DispersionInfo] | None = Field(None, min_length=1)
    dnPerfInfos: list[DnPerfInfo] | None = Field(None, min_length=1)
    svcExps: list[ServiceExperienceInfo] | None = Field(None, min_length=1)
    movBehavInfos: list[MovBehavInfo] | None = Field(None, min_length=1)
    wlanInfos: list[WlanPerformInfo] | None = Field(None, min_length=1)
    relProxInfos: list[RelProxInfo] | None = Field(None, min_length=1)
    start: DateTime | None = None
    timeStampGen: DateTime | None = None
    locArea: LocationArea5G | None = None
    pauseInd: bool | None = Field(
        None,
        description='Pause analytics consumption indication. Set to "true" to indicate the consumer to stop the consumption of the analytics. Default value is "false" if omitted.\n',
    )
    resumeInd: bool | None = Field(
        None,
        description='Resume analytics consumption indication. Set to "true" to indicate the consumer to resume the consumption of the analytics. Default value is "false" if omitted.\n',
    )
    accuInfo: AccuracyInfo | None = None
    cancelAccuInd: bool | None = Field(
        None,
        description='Indicates cancelled subscription of the analytics accuracy information. Set to "true" indicates the NWDAF cancelled subscription of analytics accuracy information as the NWDAF does not support the accuracy checking capability. Otherwise set to "false". Default value is "false" if omitted.\n',
    )
    nsiLoadLevelData: list[NsiLoadLevelInfo] | None = Field(None, min_length=1)


class AnalyticsExposureSubsc(BaseModel):
    analyEventsSubs: list[AnalyticsEventSubsc] = Field(..., min_length=1)
    analyRepInfo: ReportingInformation | None = None
    notifUri: Uri
    notifId: str
    eventNotifis: list[AnalyticsEventNotif] | None = Field(None, min_length=1)
    failEventReports: list[AnalyticsFailureEventInfo] | None = Field(None, min_length=1)
    suppFeat: SupportedFeatures | None = None
    self: Link | None = None
    requestTestNotification: bool | None = Field(
        None,
        description="Set to true by the AF to request the NEF to send a test notification as defined in clause 5.2.5.3 of 3GPP TS 29.122. Set to false or omitted otherwise.\n",
    )
    websockNotifConfig: WebsockNotifConfig | None = None


class AnalyticsEventNotification(BaseModel):
    notifId: str
    analyEventNotifs: list[AnalyticsEventNotif] = Field(..., min_length=1)
    termCause: TermCause | None = None
