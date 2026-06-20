from pydantic import BaseModel

from app.schemas.camara.location import Location


class UELocation(BaseModel):
    msisdn: str
    location: Location
