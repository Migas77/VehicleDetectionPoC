import asyncio
import logging
from datetime import timedelta
from typing import Any

import redis.asyncio as aioredis
from fastapi import APIRouter
from fastapi.responses import Response

from app.redis import RedisDep
from app.settings import settings

LOG = logging.getLogger(__name__)

router = APIRouter(prefix="/callbacks/crash_inference")

_DEBOUNCE_KEY_PREFIX = "poc:crash_inference:debounce:"
_STREAK_KEY_PREFIX = "poc:crash_inference:streak:"


@router.post("/{ue_supi}", status_code=204)
async def crash_inference_webhook(
    ue_supi: str, body: dict[str, Any], redis: RedisDep
) -> Response:
    """Receive Roboflow inference webhook. Returns 204 immediately; processing runs in background."""
    asyncio.create_task(_process_detection(ue_supi, body, redis))
    return Response(status_code=204)


async def _process_detection(
    ue_supi: str, payload: dict[str, Any], redis: aioredis.Redis
) -> None:

    detections_number: int = payload.get("detections_number", 0)
    frame_number = payload.get("frame_number")
    LOG.info(
        "Processing inference result: detections=%s, frame=%s, all=%s",
        detections_number,
        frame_number,
        payload,
    )

    streak_key = f"{_STREAK_KEY_PREFIX}{ue_supi}"
    if frame_number is None:
        LOG.error(
            "Inference payload for camera supi=%s has no frame_number",
            ue_supi,
        )
        return
    if detections_number == 0:
        await redis.delete(streak_key)
        return

    predictions: list[dict[str, Any]] = (payload.get("predictions") or {}).get(
        "predictions"
    ) or []
    matching = [
        p
        for p in predictions
        if (p.get("class") or "").lower() in settings.crash_inference.classes
        and p.get("confidence", 0.0) >= settings.crash_inference.intervention_threshold
    ]
    if not matching:
        await redis.delete(streak_key)
        return

    debounce_key = f"{_DEBOUNCE_KEY_PREFIX}{ue_supi}"
    if await redis.exists(debounce_key):
        LOG.debug(
            "Intervention debounced for camera supi=%s on frame %s (debounce=%.1fs)",
            ue_supi,
            frame_number,
            settings.crash_inference.debounce_seconds,
        )
        return

    # Require the crash detection to persist across crash_window_size frames
    max_fps = settings.cameras.get_inference_config_by_ue_supi(ue_supi).max_fps
    required_span = settings.crash_inference.crash_window_size(max_fps)
    first_frame = await redis.get(streak_key)
    if first_frame is None:
        await redis.set(streak_key, frame_number)
        return
    span = frame_number - int(first_frame)
    if span < required_span:
        return

    # Detection persisted across x frames
    # Redis reset + crash detection notification to UEs
    await redis.set(
        debounce_key,
        "1",
        ex=timedelta(seconds=settings.crash_inference.debounce_seconds),
    )
    await redis.delete(streak_key)
    LOG.warning(
        "Intervention triggered: crash persisted across frames %s..%s (span %d >= %d) "
        "for camera supi=%s (classes=%s)",
        first_frame,
        frame_number,
        span,
        required_span,
        ue_supi,
        [p["class"] for p in matching],
    )
    # TODO: implement crash detection handling (i.e. send sms to pedestrians and message to UEs)
