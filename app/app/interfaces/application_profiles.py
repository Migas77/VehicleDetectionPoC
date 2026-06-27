import logging
from abc import ABC, abstractmethod

from app.schemas.camara.application_profiles import (
    ApplicationProfile,
    ApplicationProfileId,
)
from app.schemas.poc.ue_with_qos import UeWithQoS

LOG = logging.getLogger(__name__)


class ApplicationProfilesInterface(ABC):
    @abstractmethod
    async def create_application_profile(self, ue: UeWithQoS) -> ApplicationProfile:
        """Create an application profile for the UE from its QoS settings."""

    @abstractmethod
    async def get_application_profile(
        self,
        ue_supi: str,
        application_profile_id: ApplicationProfileId | None = None,
    ) -> ApplicationProfile:
        """Return the application profile for the UE.

        For NEF: derives the profile from settings using ue_supi (application_profile_id is ignored).
        For CAMARA: fetches by application_profile_id from the API (raises if id is None).
        """

    @abstractmethod
    async def delete_application_profile(
        self, application_profile_id: ApplicationProfileId
    ) -> bool:
        """Delete the application profile by ID. Returns True on success."""
