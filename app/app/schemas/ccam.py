from pydantic import BaseModel


class ReferencePositionWithConfidence(BaseModel):
    latitude: int
    """Latitude in degrees (-90 to 90) times 10^7"""
    longitude: int
    """Longitude in degrees (-180 to 180) times 10^7"""


class BasicContainer(BaseModel):
    referencePosition: ReferencePositionWithConfidence


class MCMMessageInner(BaseModel):
    basicContainer: BasicContainer


class MCMMessage(BaseModel):
    payload: MCMMessageInner


class CPMMessageInner(BaseModel):
    managementContainer: BasicContainer


class CPMMessage(BaseModel):
    cpm: CPMMessageInner


class DENMHeader(BaseModel):
    protocolVersion: int
    messageId: int
    stationId: int


class DENMActionId(BaseModel):
    originatingStationId: int
    sequenceNumber: int


class DENMPositionConfidenceEllipse(BaseModel):
    semiMajorConfidence: int
    semiMinorConfidence: int
    semiMajorOrientation: int


class DENMAltitude(BaseModel):
    altitudeValue: int
    altitudeConfidence: str


class DENMEventPosition(BaseModel):
    latitude: int
    """Latitude in degrees (-90 to 90) times 10^7"""
    longitude: int
    """Longitude in degrees (-180 to 180) times 10^7"""
    positionConfidenceEllipse: DENMPositionConfidenceEllipse
    altitude: DENMAltitude


class DENMManagementContainer(BaseModel):
    actionId: DENMActionId
    detectionTime: int
    referenceTime: int
    eventPosition: DENMEventPosition
    relevanceDistance: str
    validityDuration: int
    transmissionInterval: int
    stationType: int


class DENMCcAndScc(BaseModel):
    accident2: int


class DENMEventType(BaseModel):
    ccAndScc: DENMCcAndScc


class DENMSituationContainer(BaseModel):
    informationQuality: int
    eventType: DENMEventType


class DENMMessageInner(BaseModel):
    management: DENMManagementContainer
    situation: DENMSituationContainer


class DENMMessage(BaseModel):
    header: DENMHeader
    denm: DENMMessageInner
