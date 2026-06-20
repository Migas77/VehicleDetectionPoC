import re
from typing import Annotated, Any, Union

from pydantic import Discriminator, Tag

from app.schemas.poc.cameras import DynamicCameraUE, StaticCameraUE
from app.schemas.poc.car import CarUE
from app.schemas.poc.pedestrian import PedestrianUE


def _ue_discriminator(v: Any) -> str:
    name: str = (
        v.get("name") if isinstance(v, dict) else getattr(v, "name", None)
    ) or ""
    if re.match(r"^car-", name):
        return "car"
    if re.match(r"^scamera-", name):
        return "scamera"
    if re.match(r"^dcamera-", name):
        return "dcamera"
    if re.match(r"^pedestrian-", name):
        return "pedestrian"
    raise ValueError(f"cannot determine UE type from name '{name}'")


PocUE = Annotated[
    Union[
        Annotated[CarUE, Tag("car")],
        Annotated[StaticCameraUE, Tag("scamera")],
        Annotated[DynamicCameraUE, Tag("dcamera")],
        Annotated[PedestrianUE, Tag("pedestrian")],
    ],
    Discriminator(_ue_discriminator),
]
