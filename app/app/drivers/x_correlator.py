import logging
import uuid
from collections.abc import Awaitable, Callable

import httpx
from pydantic import TypeAdapter

from app.schemas.camara.common import XCorrelator

LOG = logging.getLogger(__name__)

# Header name used by the CAMARA Commonalities spec (and echoed by the gateway).
X_CORRELATOR_HEADER = "x-correlator"

_x_correlator_adapter: TypeAdapter[str] = TypeAdapter(XCorrelator)


def _new_x_correlator() -> str:
    """Return a fresh correlation id (a UUIDv4) valid against the CAMARA XCorrelator schema."""
    return _x_correlator_adapter.validate_python(str(uuid.uuid4()))


async def _stamp_x_correlator(request: httpx.Request) -> None:
    """httpx request hook: stamp an x-correlator header on every outbound call.

    The generated value stays on the ``httpx.Request`` object, so callers can read
    it back for benchmarking via ``response.request.headers["x-correlator"]``.
    """
    if X_CORRELATOR_HEADER not in request.headers:
        request.headers[X_CORRELATOR_HEADER] = _new_x_correlator()


# Pass as `event_hooks` to every httpx.AsyncClient that leaves the PoC towards NEF/CAMARA.
EVENT_HOOKS: dict[str, list[Callable[[httpx.Request], Awaitable[None]]]] = {
    "request": [_stamp_x_correlator]
}
