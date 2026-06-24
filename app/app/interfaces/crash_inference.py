import logging
from abc import ABC, abstractmethod

from app.redis import get_redis
from app.schemas.poc.cameras import CameraUE

LOG = logging.getLogger(__name__)


class CrashInferenceInterface(ABC):
    def __init__(self) -> None:
        self._redis = get_redis()

    @staticmethod
    def _pipeline_key(camera_id: int) -> str:
        return f"poc_crash_inference_{camera_id}"

    @abstractmethod
    async def start_pipeline(self, camera: CameraUE) -> str | None:
        """Start the crash inference pipeline for the camera. Returns the pipeline ID, or None if inference is not enabled for this camera."""

    @abstractmethod
    async def terminate_pipeline(self, camera: CameraUE) -> None:
        """Terminate the running crash inference pipeline for the camera."""
