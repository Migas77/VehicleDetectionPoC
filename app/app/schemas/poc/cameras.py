import logging
from typing import Annotated, Any

from pydantic import Field, model_validator

from app.schemas.qos_profile import QosProfile
from app.schemas.poc.ue import UE
from app.settings import settings

LOG = logging.getLogger(__name__)


class CameraUE(UE):
    """Base for camera UEs — injects QoS profile from settings at deserialization time."""

    qos_profile: QosProfile

    @classmethod
    @model_validator(mode="before")
    def _inject_qos_profile(cls, data: Any) -> Any:
        if isinstance(data, dict) and "qos_profile" not in data:
            ue_id: int | None = data.get("id")
            profile = (
                settings.cameras.get_by_ue_id(ue_id) if ue_id is not None else None
            )
            if profile is None:
                LOG.warning(
                    "No QoS profile assignment for UE id=%s, using default", ue_id
                )
                profile = settings.cameras.default_qos_profile
            data = {**data, "qos_profile": profile.model_dump()}
        return data


class StaticCamera(CameraUE):
    name: Annotated[str, Field(pattern=r"^scamera-")]


class DynamicCamera(CameraUE):
    name: Annotated[str, Field(pattern=r"^dcamera-")]
