from app.drivers.ccam.mock.backend import MockCcamBackend
from app.settings import settings

if settings.ccam_broker.backend != "mock":
    raise RuntimeError(
        "MockCcamBackend instantiated but ccam_broker.backend isn't 'mock'"
    )

mock_ccam_interface = MockCcamBackend()
