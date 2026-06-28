from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class Speed(str, Enum):
    stationary = "STATIONARY"
    low = "LOW"
    high = "HIGH"


class UE(BaseModel):
    """Mirrors the UEhex response returned by GET /api/v1/UEs on the NEF Emulator."""

    model_config = ConfigDict(from_attributes=True)

    id: int = -1  # Because NEF Emulator doesn't return id in GET /api/v1/UEs/{supi}
    supi: Annotated[str, Field(pattern=r"^[0-9]{15,16}$")]
    name: str | None = None
    description: str | None = None
    ip_address_v4: str | None = None
    ip_address_v6: str | None = None
    mac_address: Annotated[
        str, Field(pattern=r"^([0-9a-fA-F]{2})((-[0-9a-fA-F]{2}){5})$")
    ]
    msisdn: str | None = None
    dnn: str | None = None
    mcc: int | None = None
    mnc: int | None = None
    external_identifier: str | None = None
    visiting_plmnid: str | None = None
    speed: Speed
    latitude: Annotated[float, Field(ge=-90, le=90)] | None = None
    longitude: Annotated[float, Field(ge=-180, le=180)] | None = None
    path_id: int | None = None
    gNB_id: int | None = None
    Cell_id: int | None = None
    Last_known_cell_id: int | None = None
    Initial_cell_id: int | None = None
    cell_id_hex: str | None = None
