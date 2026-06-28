from pydantic import BaseModel


class ReferencePositionWithConfidence(BaseModel):
    latitude: int
    """Latitude in degrees (-90 to 90) times 10^-7"""
    longitude: int
    """Longitude in degrees (-180 to 180) times 10^-7"""


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


# TODO: DENM schema - adapt to actual ETSI EN 302 637-3 standard and broker message format


class DENMEventPosition(BaseModel):
    latitude: int
    """Latitude in degrees (-90 to 90) times 10^-7"""
    longitude: int
    """Longitude in degrees (-180 to 180) times 10^-7"""


class DENMManagementContainer(BaseModel):
    eventPosition: DENMEventPosition


class DENMSituationContainer(BaseModel):
    # TODO: map to proper ETSI causeCode/subCauseCode or a freeText extension field
    freeText: str


class DENMMessageInner(BaseModel):
    managementContainer: DENMManagementContainer
    situationContainer: DENMSituationContainer


class DENMMessage(BaseModel):
    denm: DENMMessageInner
