import logging

from app.interfaces.ccam import CcamInterface
from app.schemas.ccam import ReferencePositionWithConfidence

LOG = logging.getLogger(__name__)


class MockCcamBackend(CcamInterface):
    """No-op CCAM backend for local development — logs instead of publishing over MQTT."""

    async def send_denm(
        self, location: ReferencePositionWithConfidence, text: str
    ) -> None:
        LOG.info(
            "[MOCK] Would publish DENM at (%d, %d): %s",
            location.latitude,
            location.longitude,
            text,
        )
