from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

import aiomqtt
from fastapi import Depends

from app.settings import settings

_client: aiomqtt.Client | None = None


@asynccontextmanager
async def mqtt_lifespan() -> AsyncGenerator[None, None]:
    global _client
    broker = settings.ccam_broker
    async with aiomqtt.Client(
        hostname=broker.host,
        port=broker.port,
        identifier=broker.client_id,
        username=broker.username,
        password=broker.password,
        transport=broker.transport,
        websocket_path=broker.ws_path if broker.transport == "websockets" else None,
    ) as client:
        _client = client
        yield
    _client = None


def get_mqtt_client() -> aiomqtt.Client:
    if _client is None:
        raise RuntimeError("MQTT client not connected — ensure mqtt_lifespan is active")
    return _client
