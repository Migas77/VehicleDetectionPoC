import logging
import uuid

from app.drivers.utilities import bitrate_str_to_rate
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
        return self._build_profile_from_qos(ue)

    async def get_application_profile(
        self,
        ue_id: int,
        application_profile_id: ApplicationProfileId | None = None,
    ) -> ApplicationProfile:
        qos_profile = settings.cameras.get_by_ue_id(ue_id)
        if qos_profile is None:
            LOG.warning("UE id=%s not found in camera settings, using default", ue_id)
            qos_profile = settings.cameras.default_qos_profile
        return ApplicationProfile(
            applicationProfileId=uuid.uuid4(),
            networkQualityThresholds=NetworkQualityThresholds(
                targetMinUpstreamRate=bitrate_str_to_rate(qos_profile.min_ul_bitrate),
                targetMinDownstreamRate=bitrate_str_to_rate(qos_profile.min_dl_bitrate),
            ),
        )

    async def delete_application_profile(
        self, application_profile_id: ApplicationProfileId
    ) -> bool:
        return True  # no-op — profile was never persisted

    @staticmethod
    def _build_profile_from_qos(ue: UeWithQoS) -> ApplicationProfile:
        return ApplicationProfile(
            applicationProfileId=uuid.uuid4(),
            networkQualityThresholds=NetworkQualityThresholds(
                targetMinUpstreamRate=bitrate_str_to_rate(
                    ue.qos_profile.min_ul_bitrate
                ),
                targetMinDownstreamRate=bitrate_str_to_rate(
                    ue.qos_profile.min_dl_bitrate
                ),
            ),
        )
