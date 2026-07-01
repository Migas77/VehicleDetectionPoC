import logging

from fastapi import APIRouter
from pydantic import AnyHttpUrl

from app.settings import NetApisSettings, settings

LOG = logging.getLogger(__name__)

router = APIRouter(prefix="/config")


@router.get("/net-apis")
async def get_net_apis_config() -> NetApisSettings:
    """Expose the currently configured network API mode and authentication mode."""
    return settings.net_apis


@router.get("/inference-server")
async def get_inference_server_config() -> AnyHttpUrl:
    """Expose the currently configured crash inference server URL."""
    return settings.crash_inference.inference_server_url
