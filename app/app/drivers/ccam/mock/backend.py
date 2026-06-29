import logging

from app.interfaces.ccam import CcamInterface
from app.schemas.poc.crash_status import CrashLocation

LOG = logging.getLogger(__name__)


class MockCcamBackend(CcamInterface):
    """No-op CCAM backend for local development — logs instead of publishing over MQTT."""

    async def send_denm(self, location: CrashLocation) -> None:
        LOG.info(
            "[MOCK] Would publish DENM at (%d, %d)",
            int(location.latitude * 10_000_000),
            int(location.longitude * 10_000_000),
        )
