import logging
from typing import Annotated, Literal

from pydantic import AnyHttpUrl, BaseModel, Field, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]


class NetApisSettings(BaseModel):
    api: Literal["camara", "nef"]
    auth_mode: Literal["capif", "other"]


class NefSettings(BaseModel):
    url: AnyHttpUrl
    username: str | None = None
    password: str | None = None


class CamaraSettings(BaseModel):
    url: AnyHttpUrl


class CapifSdkSettings(BaseModel):
    capif_username: str
    capif_password: str


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
    model_config = SettingsConfigDict(toml_file="config.toml")

    poc_public_url: AnyHttpUrl
    poc_af_id: str
    log_level: LogLevel = "INFO"

    net_apis: NetApisSettings
    nef: NefSettings
    camara: CamaraSettings | None = None
    capif_sdk: CapifSdkSettings | None = None
    analytics: AnalyticsSettings

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
            TomlConfigSettingsSource(settings_cls),
        )


settings = Settings()

logging.basicConfig(level=settings.log_level)
