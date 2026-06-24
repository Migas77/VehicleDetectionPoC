import logging
from functools import cached_property
from typing import cast

import httpx

from app.drivers.crash_inference.callbacks import router as callbacks_router
from app.interfaces.crash_inference import CrashInferenceInterface
from app.schemas.poc.cameras import CameraUE
from app.settings import settings

LOG = logging.getLogger(__name__)


def _build_workflow_specification(camera_id: int) -> dict[str, object]:
    return {
        "version": "1.0",
        "inputs": [
            {"type": "WorkflowImage", "name": "image"},
        ],
        "steps": [
            # Perform object detection using the specified model
            {
                "type": "roboflow_core/roboflow_object_detection_model@v2",
                "name": "model",
                "image": "$inputs.image",
                "model_id": settings.crash_inference.model_id,
            },
            # Add bounding boxes and labels to the image for visualization
            {
                "type": "roboflow_core/bounding_box_visualization@v1",
                "name": "bounding_box",
                "predictions": "$steps.model.predictions",
                "image": "$inputs.image",
            },
            {
                "type": "roboflow_core/label_visualization@v1",
                "name": "visualization",
                "predictions": "$steps.model.predictions",
                "image": "$steps.bounding_box.image",
                "text": "Class and Confidence",
                "text_scale": 0.4,
                "text_thickness": 1,
            },
            # Call webhook to send the annotated predictions to the webhook endpoint
            # And trigger appropriate actions on the backend
            {
                "type": "roboflow_core/webhook_sink@v1",
                "name": "webhook",
                "url": f"{str(settings.crash_inference.poc_notification_url).rstrip('/')}{callbacks_router.prefix}/{camera_id}",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "json_payload": {
                    "detections_number": "$steps.model.predictions",
                    "predictions": "$steps.model.predictions",
                    "frame_number": "$inputs.image",
                },
                "json_payload_operations": {
                    "detections_number": [{"type": "SequenceLength"}],
                    "predictions": [{"type": "DetectionsToDictionary"}],
                    "frame_number": [
                        {
                            "type": "ExtractFrameMetadata",
                            "property_name": "frame_number",
                        }
                    ],
                },
                "cooldown_seconds": 0,
                "fire_and_forget": True,
            },
        ],
        "outputs": [
            # Outputs for the inference pipeline, including the predictions and the annotated image
            # To consume the endpoint at /inference_pipelines/{pipeline_id}/consume and display results in the UI
            {
                "type": "JsonField",
                "name": "preview",
                "selector": "$steps.visualization.image",
            },
            {
                "type": "JsonField",
                "name": "predictions",
                "coordinates_system": "own",
                "selector": "$steps.model.predictions",
            },
            {
                "type": "JsonField",
                "name": "detections_number",
                "selector": "$steps.model.predictions",
                "json_operations": [{"type": "SequenceLength"}],
            },
            {
                "type": "JsonField",
                "name": "frame_number",
                "selector": "$inputs.image",
                "json_operations": [
                    {
                        "type": "ExtractFrameMetadata",
                        "property_name": "frame_number",
                    }
                ],
            },
        ],
    }


class RoboflowCrashInferenceBackend(CrashInferenceInterface):
    """Starts and terminates Roboflow inference pipelines via the Inference Server HTTP API."""

    @cached_property
    def _client(self) -> httpx.AsyncClient:
        # No timeout as the inference pipeline API may take a long time to respond
        return httpx.AsyncClient(
            base_url=str(settings.crash_inference.inference_server_url).rstrip("/"),
            timeout=None,
        )

    async def start_pipeline(self, camera: CameraUE) -> str | None:
        inference_config = settings.cameras.get_inference_config_by_ue_id(camera.id)
        if not inference_config.inference_enabled:
            LOG.debug("Inference not enabled for camera id=%s, skipping", camera.id)
            return None

        # validator guarantees video_reference is set when inference_enabled=True
        video_reference = inference_config.video_reference
        LOG.info(
            "Starting crash inference pipeline (camera_id=%s, model=%s, video=%s)",
            camera.id,
            settings.crash_inference.model_id,
            video_reference,
        )
        payload = {
            "api_key": settings.roboflow.api_key,
            "video_configuration": {
                "type": "VideoConfiguration",
                "video_reference": video_reference,
                "max_fps": inference_config.max_fps,
            },
            "processing_configuration": {
                "type": "WorkflowConfiguration",
                "workflow_specification": _build_workflow_specification(camera.id),
            },
            "sink_configuration": {
                "type": "MemorySinkConfiguration",
            },
        }
        res = await self._client.post("/inference_pipelines/initialise", json=payload)
        if not res.is_success:
            raise RuntimeError(
                f"Failed to start inference pipeline for camera id={camera.id} "
                f"({res.status_code}): {res.text}"
            )

        data = res.json()
        pipeline_id: str = data["context"]["pipeline_id"]
        await self._redis.set(self._pipeline_key(camera.id), pipeline_id)
        LOG.info(
            "Crash inference pipeline started, camera_id=%s, pipeline_id=%s",
            camera.id,
            pipeline_id,
        )
        return pipeline_id

    async def terminate_pipeline(self, camera: CameraUE) -> None:
        pipeline_id = cast(
            str | None, await self._redis.get(self._pipeline_key(camera.id))
        )
        if pipeline_id is None:
            LOG.warning(
                "No running inference pipeline found for camera id=%s", camera.id
            )
            return
        LOG.info(
            "Terminating crash inference pipeline id=%s for camera id=%s",
            pipeline_id,
            camera.id,
        )

        res = await self._client.post(
            f"/inference_pipelines/{pipeline_id}/terminate",
        )
        if res.status_code != 404 and not res.is_success:
            raise RuntimeError(
                f"Failed to terminate inference pipeline {pipeline_id} "
                f"({res.status_code}): {res.text}"
            )

        await self._redis.delete(self._pipeline_key(camera.id))
        LOG.info(
            "Crash inference pipeline terminated, camera_id=%s, pipeline_id=%s",
            camera.id,
            pipeline_id,
        )
