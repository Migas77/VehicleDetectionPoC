import json
import logging
import math
import ssl
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

import httpx

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    Field,
    PositiveInt,
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

from app.capif import (
    CAMARA_CAPIF_API_NAME,
    CAPIF_SDK_CONFIG_PATH,
    NEF_CAPIF_API_NAME,
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
    capif_host: str = "capifcore"
    register_host: str = "capifcore"
    capif_https_port: PositiveInt = 443
    capif_register_port: PositiveInt = 8084
    debug_mode: bool = True
    capif_username: str
    capif_password: str
    capif_callback_url: str = "http://your-callback-host/callback/"
    cleanup_on_shutdown: bool = False

    @model_validator(mode="after")
    def fill_json_opencapif_sdk_config(self) -> "CapifSdkSettings":
        """Push the deployment settings into the config file the OpenCAPIF SDK reads."""
        config_path = Path(CAPIF_SDK_CONFIG_PATH)
        config = json.loads(config_path.read_text())
        config.update(
            {
                "capif_host": self.capif_host,
                "register_host": self.register_host,
                "capif_https_port": str(self.capif_https_port),
                "capif_register_port": str(self.capif_register_port),
                "debug_mode": str(self.debug_mode),
                "capif_username": self.capif_username,
                "capif_password": self.capif_password,
            }
        )
        config["invoker"]["capif_callback_url"] = self.capif_callback_url
        config_path.write_text(json.dumps(config, indent=4))
        return self


class SurveyedAreaConfig(BaseModel):
    radius: Annotated[int, Field(ge=1, le=200000)]  # metres
    points: list[Point] | None = None  # optional polygon vertices (NEF refinement)


class CameraInferenceConfig(BaseModel):
    inference_enabled: bool = False
    stream_protocol: str | None = None
    stream_ip: str | None = None
    stream_port: int | None = None
    stream_path: str | None = None
    max_fps: int = 15

    @model_validator(mode="after")
    def _validate_when_enabled(self) -> "CameraInferenceConfig":
        if self.inference_enabled and (
            self.stream_protocol is None
            or self.stream_ip is None
            or self.stream_port is None
            or self.stream_path is None
        ):
            raise ValueError(
                "stream_protocol, stream_ip, stream_port and stream_path are "
                "required when inference_enabled=true"
            )
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

    def get_enabled_inference_by_ue_supi(
        self, ue_supi: str
    ) -> tuple[str, CameraInferenceConfig] | None:
        """Return (video_reference, inference_config) if inference is enabled for this camera.

        The video_reference URL is built from the inference config's stream fields.
        Returns None unless inference is enabled for this camera — validator
        guarantees stream_protocol/ip/port/path are set whenever inference_enabled=True.
        """
        inference_config = self.get_inference_config_by_ue_supi(ue_supi)
        if not inference_config.inference_enabled:
            return None
        video_reference = (
            f"{inference_config.stream_protocol}://{inference_config.stream_ip}:"
            f"{inference_config.stream_port}/{inference_config.stream_path}"
        )
        return video_reference, inference_config


class CcamBrokerSettings(BaseModel):
    backend: Literal["mqtt", "mock"] = "mock"

    client_id: str = "vehicle-crash-detection-poc"

    host: str = "es-broker.av.it.pt"
    port: int = 8090

    username: str | None = None
    password: str | None = None

    transport: Literal["tcp", "websockets", "unix"] = "tcp"
    ws_path: str = "/WS"

    topic_base_path: str = "its_center/inqueue/json"
    station_id: int = 141414
    validity_duration: int = 120  # seconds


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
        env_nested_delimiter="__",
    )

    poc_title: str
    poc_af_id: str
    poc_app_server: str
    log_level: LogLevel = "INFO"
    cors_allow_origins: list[str]

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

        if self.nef is None:
            raise ValueError("[nef] section required")

        # Required in both auth modes and for both APIs: the NEF management APIs
        # (/api/v1/...) are not published to CAPIF, so the PoC always calls them
        # (UEs, movement, QoS characteristics) with the NEF login
        if not self.nef.username or not self.nef.password:
            raise ValueError("nef.username and nef.password required")

        if auth_mode == "capif" and self.capif_sdk is None:
            raise ValueError(
                "[capif_sdk] section required when net_apis.auth_mode = 'capif'"
            )

        return self

    def _get_ssl_context(self) -> ssl.SSLContext | bool:
        """Build the mTLS context the AEFs (NEF / gateway nginx) require from CAPIF invokers."""
        if self.net_apis.auth_mode != "capif":
            return False

        from app.capif.invoker import capif_invoker  # deferred — avoids circular import

        if capif_invoker.invoker is None:
            raise RuntimeError(
                "CAPIF invoker is not initialized: its certificates are only available "
                "after onboarding (capif_invoker.startup())"
            )

        ssl_context = ssl.create_default_context(cafile=capif_invoker.invoker.pathca)
        ssl_context.load_cert_chain(
            certfile=capif_invoker.invoker.signed_key_crt_path,
            keyfile=capif_invoker.invoker.private_key_path,
        )
        # The AEF certificate is issued for its CAPIF-internal hostname, which is not
        # the address the invoker reaches it on (discovery hands back an IP/fqdn)
        ssl_context.check_hostname = False
        return ssl_context

    def create_nef_auth_client(self) -> httpx.AsyncClient:
        """Return an AsyncClient for the NEF management APIs (/api/v1/...) with JWT bearer auth.

        These are NOT published to CAPIF (the NEF only publishes its northbound
        3gpp-* APIs), so they keep using the NEF login even in capif auth_mode —
        only the mTLS client certificate is added there, as the NEF's nginx
        requires one from every caller.

        Settings validator guarantees username/password are set.
        """
        from app.drivers.nef_auth import NEFJwtAuth  # deferred — avoids circular import

        nef_url = str(self.nef.url).rstrip("/")
        auth: httpx.Auth = NEFJwtAuth(
            nef_url,
            self.nef.username,  # type: ignore[arg-type]  # guaranteed by validator
            self.nef.password,  # type: ignore[arg-type]
        )
        return httpx.AsyncClient(
            base_url=nef_url, auth=auth, verify=self._get_ssl_context()
        )

    def create_nef_exposure_client(self) -> httpx.AsyncClient:
        """Return an AsyncClient for the NEF northbound APIs (/nef/api/v1/3gpp-...).

        In capif auth_mode these are invoked as a CAPIF API invoker: the AEF endpoint
        comes from service discovery and the requests carry the CAPIF access token,
        instead of the configured url and the NEF login.
        """
        if self.net_apis.auth_mode != "capif":
            return self.create_nef_auth_client()

        from app.capif.invoker import capif_invoker  # deferred — avoids circular import
        from app.drivers.capif_auth import CAPIFAuth

        return httpx.AsyncClient(
            base_url=capif_invoker.get_base_url(NEF_CAPIF_API_NAME),
            auth=CAPIFAuth(),
            verify=self._get_ssl_context(),
        )

    def create_camara_client(self) -> httpx.AsyncClient:
        """Return an AsyncClient for the CAMARA gateway.

        In capif auth_mode the gateway protects its CAMARA APIs with CAPIF, so the
        endpoint is discovered and the requests carry the CAPIF access token.

        Settings validator guarantees camara is not None when net_apis.api='camara'.
        """
        if self.camara is None:
            raise RuntimeError(
                "[camara] settings required — ensure net_apis.api = 'camara' and "
                "[camara] section is present in config.toml"
            )

        if self.net_apis.auth_mode != "capif":
            return httpx.AsyncClient(
                base_url=str(self.camara.url).rstrip("/"),
                verify=self._get_ssl_context(),
            )

        from app.capif.invoker import capif_invoker  # deferred — avoids circular import
        from app.drivers.capif_auth import CAPIFAuth

        return httpx.AsyncClient(
            base_url=capif_invoker.get_base_url(CAMARA_CAPIF_API_NAME),
            auth=CAPIFAuth(),
            verify=self._get_ssl_context(),
        )

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
