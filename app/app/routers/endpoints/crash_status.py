import logging
from uuid import UUID

from fastapi import APIRouter

from app.drivers.crash_status import CrashStatusBrokerDep
from app.schemas.poc.crash_status import CrashStatusEvent

LOG = logging.getLogger(__name__)

router = APIRouter(prefix="/crash-status")


@router.get("/incidents")
async def list_incidents(
    broker: CrashStatusBrokerDep,
    limit: int = 50,
    offset: int = 0,
) -> list[CrashStatusEvent]:
    """List incidents most-recent first, returning the DETECTED event for each."""
    return await broker.list_incidents(offset=offset, limit=limit)


@router.get("/incidents/{incident_id}")
async def get_incident(
    incident_id: UUID,
    broker: CrashStatusBrokerDep,
) -> list[CrashStatusEvent]:
    """Return all events recorded for a given incident, in chronological order."""
    return await broker.get_incident(str(incident_id))
