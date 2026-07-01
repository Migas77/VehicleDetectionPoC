import logging
from typing import Annotated, Any

from pydantic import BaseModel, Field, model_validator

from app.schemas.poc.ue_with_qos import UeWithQoS
from app.schemas.qos_profile import QosProfile
from app.settings import CameraInferenceConfig, SurveyedAreaConfig, settings

LOG = logging.getLogger(__name__)


class CameraUE(UeWithQoS):
    ""

    "Base for camera UEs — injects QoS profile from settings at deserialization time."

    @model_validator(mode="before")
    @classmethod
    def _inject_qos_profile(cls, data: Any) -> Any:
        if isinstance(data, dict) and "qos_profile" not in data:
            ue_supi: str | None = data["supi"]
            profile = (
                settings.cameras.get_by_ue_supi(ue_supi)
                if ue_supi is not None
                else None
            )
            if profile is None:
                LOG.warning(
                    "No QoS profile assignment for UE supi=%s, using default", ue_supi
                )
                profile = settings.cameras.default_qos_profile
            data = {**data, "qos_profile": profile.model_dump()}
            return data
        raise ValueError("CameraUE deserialization expects a dict")


class StaticCameraUE(CameraUE):
    name: Annotated[str, Field(pattern=r"^scamera-")]


class DynamicCameraUE(CameraUE):
    name: Annotated[str, Field(pattern=r"^dcamera-")]


class CameraInfo(BaseModel):
    """Full per-camera configuration, as resolved from cameras.toml."""

    ue_supi: str
    qos_profile: QosProfile
    surveyed_area: SurveyedAreaConfig
    inference: CameraInferenceConfig
