import logging
import uuid

from app.utilities import bitrate_str_to_rate
from app.interfaces.application_profiles import ApplicationProfilesInterface
from app.schemas.camara.application_profiles import (
    ApplicationProfile,
    ApplicationProfileId,
    NetworkQualityThresholds,
)
from app.schemas.poc.ue_with_qos import UeWithQoS
from app.settings import settings

LOG = logging.getLogger(__name__)


class NefApplicationProfilesBackend(ApplicationProfilesInterface):
    """Derives ApplicationProfile in-memory from settings — no NEF API call."""

    async def create_application_profile(self, ue: UeWithQoS) -> ApplicationProfile:
        return self._build_profile_from_stream_requirements(ue.supi)

    async def get_application_profile(
        self,
        ue_supi: str,
        application_profile_id: ApplicationProfileId | None = None,
    ) -> ApplicationProfile:
        return self._build_profile_from_stream_requirements(ue_supi)

    async def delete_application_profile(
        self, application_profile_id: ApplicationProfileId
    ) -> bool:
        return True  # no-op — profile was never persisted

    @staticmethod
    def _build_profile_from_stream_requirements(ue_supi: str) -> ApplicationProfile:
        requirements = settings.cameras.get_stream_requirements_by_ue_supi(ue_supi)
        if requirements is None:
            LOG.warning(
                "UE supi=%s not found in camera settings, using default", ue_supi
            )
            requirements = settings.cameras.default_stream_requirements
        return ApplicationProfile(
            applicationProfileId=uuid.uuid4(),
            networkQualityThresholds=NetworkQualityThresholds(
                targetMinUpstreamRate=bitrate_str_to_rate(requirements.min_ul_bitrate),
                targetMinDownstreamRate=bitrate_str_to_rate(
                    requirements.min_dl_bitrate
                ),
            ),
        )
