from enum import Enum

from pydantic import BaseModel

from app.schemas.camara.location import Location
from app.schemas.poc.poc_ue import PocUE


class UEType(str, Enum):
    car = "car"
    camera = "camera"
    pedestrian = "pedestrian"


class UELocation(BaseModel):
    ue: PocUE
    type: UEType
    location: Location
