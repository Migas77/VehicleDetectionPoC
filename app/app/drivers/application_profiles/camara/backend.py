import logging
from functools import cached_property

import httpx

from app.drivers.utilities import bitrate_str_to_rate
from app.drivers.capif_auth import discover_camara_url
from app.interfaces.application_profiles import ApplicationProfilesInterface
from app.schemas.camara.application_profiles import (
    ApplicationProfile,
    ApplicationProfileId,
    ApplicationProfileRequest,
    NetworkQualityThresholds,
)
from app.schemas.poc.ue_with_qos import UeWithQoS
from app.settings import settings

LOG = logging.getLogger(__name__)


class CamaraApplicationProfilesBackend(ApplicationProfilesInterface):
    """Creates and retrieves ApplicationProfiles via the CAMARA Application Profiles API."""

    @cached_property
    def _client(self) -> httpx.AsyncClient:
        return settings.create_camara_client()

    async def create_application_profile(self, ue: UeWithQoS) -> ApplicationProfile:
        payload = ApplicationProfileRequest(
            networkQualityThresholds=NetworkQualityThresholds(
                targetMinUpstreamRate=bitrate_str_to_rate(
                    ue.qos_profile.min_ul_bitrate
                ),
                targetMinDownstreamRate=bitrate_str_to_rate(
                    ue.qos_profile.min_dl_bitrate
                ),
            ),
        )
        LOG.info("Creating CAMARA ApplicationProfile for UE supi=%s", ue.supi)
        res = await self._client.post(
            discover_camara_url(
                fallback="/application-profiles/v0.5/application-profiles",
                resource_name="Create Application Profile",
                api_name_filter="application-profiles",
                operation="POST",
            ),
            content=payload.model_dump_json(exclude_unset=True),
            headers={"Content-Type": "application/json"},
        )
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA ApplicationProfile creation failed ({res.status_code}): {res.text}"
            )
        profile = ApplicationProfile.model_validate_json(res.content)
        LOG.info(
            "CAMARA ApplicationProfile created for UE supi=%s, id=%s",
            ue.supi,
            profile.applicationProfileId,
        )
        return profile

    async def get_application_profile(
        self,
        ue_supi: str,
        application_profile_id: ApplicationProfileId | None = None,
    ) -> ApplicationProfile:
        if application_profile_id is None:
            raise RuntimeError(
                f"CAMARA ApplicationProfile get requires application_profile_id for UE supi={ue_supi}"
            )
        res = await self._client.get(
            discover_camara_url(
                fallback="/application-profiles/v0.5/application-profiles/{applicationProfileId}",
                resource_name="Get Application Profile By Id",
                api_name_filter="application-profiles",
                operation="GET",
            ).format(applicationProfileId=application_profile_id)
        )
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA ApplicationProfile get failed ({res.status_code}): {res.text}"
            )
        return ApplicationProfile.model_validate_json(res.content)

    async def delete_application_profile(
        self, application_profile_id: ApplicationProfileId
    ) -> bool:
        LOG.info("Deleting CAMARA ApplicationProfile id=%s", application_profile_id)
        res = await self._client.delete(
            discover_camara_url(
                fallback="/application-profiles/v0.5/application-profiles/{applicationProfileId}",
                resource_name="Delete Application Profile By Id",
                api_name_filter="application-profiles",
                operation="DELETE",
            ).format(applicationProfileId=application_profile_id)
        )
        if res.status_code == 404:
            LOG.warning(
                "CAMARA ApplicationProfile id=%s not found for deletion",
                application_profile_id,
            )
            return False
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA ApplicationProfile delete failed ({res.status_code}): {res.text}"
            )
        LOG.info("CAMARA ApplicationProfile id=%s deleted", application_profile_id)
        return True
