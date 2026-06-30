import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.drivers.crash_status import CrashStatusBrokerDep
from app.schemas.poc.crash_status import CrashStatusEvent

LOG = logging.getLogger(__name__)

router = APIRouter(prefix="/crash-status")


@router.get("/events")
async def list_events(
    broker: CrashStatusBrokerDep,
    limit: int = 50,
    offset: int = 0,
    before: datetime | None = Query(default=None),
) -> list[CrashStatusEvent]:
    """List all crash status events, most-recent first."""
    if before is not None:
        if before.tzinfo is None:
            before = before.replace(tzinfo=timezone.utc)
        if before > datetime.now(timezone.utc):
            raise HTTPException(
                status_code=422, detail="`before` must not be a future datetime"
            )
    return await broker.list_events(before=before, offset=offset, limit=limit)


@router.get("/incidents/{incident_id}")
async def get_incident(
    incident_id: UUID,
    broker: CrashStatusBrokerDep,
) -> list[CrashStatusEvent]:
    """Return all events recorded for a given incident, in chronological order."""
    return await broker.get_incident(str(incident_id))
