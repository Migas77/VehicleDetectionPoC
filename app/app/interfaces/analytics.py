import logging
from abc import ABC, abstractmethod

from app.schemas.camara.application_profiles import ApplicationProfileId
from app.schemas.poc.ue_with_qos import UeWithQoS

LOG = logging.getLogger(__name__)


class AnalyticsInterface(ABC):
    @abstractmethod
    async def create_analytics_subscription(
        self, ue: UeWithQoS, application_profile_id: ApplicationProfileId
    ) -> str:
        """Subscribe to network analytics for the UE. Returns the subscription ID."""

    @abstractmethod
    async def delete_analytics_subscription(self, subscription_id: str) -> bool:
        """Delete an analytics subscription by ID. Returns True on success."""
