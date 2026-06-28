import logging

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from app.drivers.crash_status import CrashStatusBrokerDep

LOG = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/crash-status")
async def stream_crash_status(
    websocket: WebSocket, broker: CrashStatusBrokerDep
) -> None:
    """Stream crash notification status events (DETECTED, SENT) to connected clients."""
    await websocket.accept()
    queue = broker.subscribe()
    try:
        while True:
            event = await queue.get()
            await websocket.send_text(event.model_dump_json())
    except WebSocketDisconnect:
        LOG.info("Crash-status WebSocket client disconnected")
    finally:
        broker.unsubscribe(queue)
