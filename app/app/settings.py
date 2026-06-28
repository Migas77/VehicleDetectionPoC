import logging
import math
from functools import lru_cache
from typing import Annotated, Literal

import httpx

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    Field,
    RedisDsn,
    field_validator,
    model_validator,
)
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from app.schemas.camara.common import Point
from app.schemas.qos_profile import QosProfile


LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]


class NetApisSettings(BaseModel):
    api: Literal["camara", "nef"]
    auth_mode: Literal["capif", "other"]


class NefSettings(BaseModel):
    url: AnyHttpUrl
    poc_notification_url: AnyHttpUrl
    username: str | None = None
    password: str | None = None


class CamaraSettings(BaseModel):
    url: AnyHttpUrl
    poc_notification_url: AnyHttpUrl


class CapifSdkSettings(BaseModel):
    capif_username: str
    capif_password: str


class SurveyedAreaConfig(BaseModel):
    radius: Annotated[int, Field(ge=1, le=200000)]  # metres
    points: list[Point] | None = None  # optional polygon vertices (NEF refinement)


class CameraInferenceConfig(BaseModel):
    inference_enabled: bool = False
    video_reference: str | None = None
    max_fps: int = 15

    @model_validator(mode="after")
    def _validate_when_enabled(self) -> "CameraInferenceConfig":
        if self.inference_enabled and self.video_reference is None:
            raise ValueError("video_reference is required when inference_enabled=true")
        return self


class CamerasSettings(BaseModel):
    qos_profiles: dict[str, QosProfile]  # {profile_name : QosProfile}
    qos_profiles_assignment: dict[str, str]  # {"default" / ue_supi : profile_name}
    surveyed_areas: dict[
        str, SurveyedAreaConfig
    ]  # {"default" / ue_supi : SurveyedAreaConfig}
    inference: dict[str, CameraInferenceConfig] = Field(
        default_factory=dict
    )  # {"default" / ue_supi : CameraInferenceConfig}

    @model_validator(mode="after")
    def _validate_qos_profile_assignments(self) -> "CamerasSettings":
        if "default" not in self.qos_profiles_assignment:
            raise ValueError("qos_profiles_assignment must contain a 'default' key")
        for key, name in self.qos_profiles_assignment.items():
            if name not in self.qos_profiles:
                raise ValueError(
                    f"qos_profiles_assignment['{key}'] references unknown profile '{name}'. "
                    f"Valid names: {sorted(self.qos_profiles)}"
                )
        return self

    @model_validator(mode="after")
    def _validate_surveyed_areas(self) -> "CamerasSettings":
        if "default" not in self.surveyed_areas:
            raise ValueError("surveyed_areas must contain a 'default' key")
        return self

    @property
    def default_qos_profile(self) -> QosProfile:
        return self.qos_profiles[self.qos_profiles_assignment["default"]]

    def get_by_ue_supi(self, ue_supi: str) -> QosProfile | None:
        name = self.qos_profiles_assignment.get(ue_supi)
        if name is None:
            return None
        return self.qos_profiles[name]  # validator guarantees name exists

    @property
    def default_surveyed_area(self) -> SurveyedAreaConfig:
        return self.surveyed_areas["default"]  # validator guarantees presence

    def get_area_by_ue_supi(self, ue_supi: str) -> SurveyedAreaConfig | None:
        return self.surveyed_areas.get(ue_supi)

    def get_inference_config_by_ue_supi(self, ue_supi: str) -> CameraInferenceConfig:
        return (
            self.inference.get(ue_supi)
            or self.inference.get("default")
            or CameraInferenceConfig()
        )


class CcamBrokerSettings(BaseModel):
    client_id: str = "vehicle-crash-detection-poc"

    host: str = "es-broker.av.it.pt"
    port: int = 8090

    username: str | None = None
    password: str | None = None

    transport: Literal["tcp", "websockets", "unix"] = "tcp"
    ws_path: str = "/WS"

    topic_base_path: str = "its_center/inqueue/json"


class RoboflowSettings(BaseModel):
    api_key: str


class RedisSettings(BaseModel):
    url: RedisDsn = RedisDsn("redis://localhost:6379")
    username: str | None = None
    password: str | None = None


class CrashInferenceSettings(BaseModel):
    model_id: str
    classes: set[str]
    debounce_seconds: Annotated[float, Field(gt=0.0)]
    intervention_threshold: Annotated[float, Field(gt=0.0, lt=1.0)]
    average_car_crash_duration: Annotated[float, Field(gt=0.0)]
    inference_server_url: AnyHttpUrl
    poc_notification_url: AnyHttpUrl

    @field_validator("classes", mode="after")
    @classmethod
    def _normalize_classes(cls, v: set[str]) -> set[str]:
        return {c.lower() for c in v}

    @staticmethod
    @lru_cache(maxsize=None)
    def _compute_window_size(average_car_crash_duration: float, max_fps: int) -> int:
        return max(1, math.ceil(average_car_crash_duration * max_fps))

    def crash_window_size(self, max_fps: int) -> int:
        """Number of frames in the crash-detection sliding window for a given camera fps."""
        return self._compute_window_size(self.average_car_crash_duration, max_fps)


class AnalyticsSettings(BaseModel):
    offset_period: Annotated[int, Field(le=-1)]  # negative (historic data) - in seconds
    temporal_gran_size: Annotated[int, Field(ge=1)]  # in seconds
    rep_period: Annotated[int, Field(ge=1)]  # in seconds

    @model_validator(mode="after")
    def validate_temporal_gran_size(self) -> "AnalyticsSettings":
        if self.temporal_gran_size < abs(self.offset_period):
            raise ValueError("temporal_gran_size must be >= abs(offset_period)")
        return self


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        toml_file=["config.toml", "cameras.toml"],
        env_file=".env",
    )

    poc_title: str
    poc_af_id: str
    poc_app_server: str
    log_level: LogLevel = "INFO"

    roboflow: RoboflowSettings

    net_apis: NetApisSettings
    nef: NefSettings
    camara: CamaraSettings | None = None
    capif_sdk: CapifSdkSettings | None = None
    analytics: AnalyticsSettings
    cameras: CamerasSettings
    crash_inference: CrashInferenceSettings
    redis: RedisSettings = Field(default_factory=RedisSettings)
    ccam_broker: CcamBrokerSettings = Field(default_factory=CcamBrokerSettings)

    @model_validator(mode="after")
    def validate_required_sections(self) -> "Settings":
        api = self.net_apis.api
        auth_mode = self.net_apis.auth_mode

        if api == "camara" and self.camara is None:
            raise ValueError("[camara] section required when net_apis.api = 'camara'")

        if api == "nef":
            if self.nef is None:
                raise ValueError("[nef] section required when net_apis.api = 'nef'")
            if auth_mode == "other" and (
                not self.nef.username or not self.nef.password
            ):
                raise ValueError(
                    "nef.username and nef.password required when net_apis.auth_mode = 'other'"
                )

        if auth_mode == "capif" and self.capif_sdk is None:
            raise ValueError(
                "[capif_sdk] section required when net_apis.auth_mode = 'capif'"
            )

        return self

    def create_nef_client(self) -> httpx.AsyncClient:
        """Return a plain AsyncClient for the NEF (no auth)."""
        return httpx.AsyncClient(base_url=str(self.nef.url).rstrip("/"))

    def create_nef_auth_client(self) -> httpx.AsyncClient:
        """Return an AsyncClient for the NEF with JWT bearer auth.

        Settings validator guarantees username/password are set when auth_mode='other'.
        """
        from app.drivers.nef_auth import NEFJwtAuth  # deferred — avoids circular import

        nef_url = str(self.nef.url).rstrip("/")
        if self.net_apis.auth_mode == "other":
            auth: httpx.Auth = NEFJwtAuth(
                nef_url,
                self.nef.username,  # type: ignore[arg-type]  # guaranteed by validator
                self.nef.password,  # type: ignore[arg-type]
            )
        else:
            raise NotImplementedError(
                f"NEF auth_mode '{self.net_apis.auth_mode}' is not yet implemented"
            )
        return httpx.AsyncClient(base_url=nef_url, auth=auth)

    def create_camara_client(self) -> httpx.AsyncClient:
        """Return an AsyncClient for the CAMARA gateway.

        Settings validator guarantees camara is not None when net_apis.api='camara'.
        """
        if self.camara is None:
            raise RuntimeError(
                "[camara] settings required — ensure net_apis.api = 'camara' and "
                "[camara] section is present in config.toml"
            )
        return httpx.AsyncClient(base_url=str(self.camara.url).rstrip("/"))

    @property
    def camara_notification_url(self) -> str:
        """Return the CAMARA notification URL. Settings validator guarantees camara is not None."""
        if self.camara is None:
            raise RuntimeError(
                "[camara] settings required — ensure net_apis.api = 'camara' and "
                "[camara] section is present in config.toml"
            )
        return str(self.camara.poc_notification_url).rstrip("/")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            env_settings,
            DotEnvSettingsSource(settings_cls),
            TomlConfigSettingsSource(settings_cls),
        )


settings = Settings()

logging.basicConfig(level=settings.log_level)
