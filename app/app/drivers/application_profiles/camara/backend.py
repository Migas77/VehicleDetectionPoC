import logging

from app.drivers.utilities import bitrate_str_to_rate
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

    def __init__(self) -> None:
        self._client = settings.create_camara_client()

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
        LOG.info("Creating CAMARA ApplicationProfile for UE id=%s", ue.id)
        res = await self._client.post(
            "/application-profiles/v0.5/application-profiles",
            content=payload.model_dump_json(exclude_unset=True),
            headers={"Content-Type": "application/json"},
        )
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA ApplicationProfile creation failed ({res.status_code}): {res.text}"
            )
        profile = ApplicationProfile.model_validate_json(res.content)
        LOG.info(
            "CAMARA ApplicationProfile created for UE id=%s, id=%s",
            ue.id,
            profile.applicationProfileId,
        )
        return profile

    async def get_application_profile(
        self,
        ue_id: int,
        application_profile_id: ApplicationProfileId | None = None,
    ) -> ApplicationProfile:
        if application_profile_id is None:
            raise RuntimeError(
                f"CAMARA ApplicationProfile get requires application_profile_id for UE id={ue_id}"
            )
        res = await self._client.get(
            f"/application-profiles/v0.5/application-profiles/{application_profile_id}"
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
            f"/application-profiles/v0.5/application-profiles/{application_profile_id}"
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
