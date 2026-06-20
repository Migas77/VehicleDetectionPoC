from typing import Annotated

from pydantic import Field

from app.schemas.poc.ue import UE


class PedestrianUE(UE):
    name: Annotated[str, Field(pattern=r"^pedestrian-")]
