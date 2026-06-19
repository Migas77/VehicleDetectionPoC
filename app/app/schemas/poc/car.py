from typing import Annotated

from pydantic import Field

from app.schemas.poc.ue import UE


class Car(UE):
    name: Annotated[str, Field(pattern=r"^car-")]
