from typing import Annotated

import paho.mqtt.client as mqtt
from fastapi import Depends
from paho.mqtt.enums import CallbackAPIVersion

from app.settings import settings


_broker = settings.ccam_broker

_mqtt_client: mqtt.Client = mqtt.Client(
    CallbackAPIVersion.VERSION2,
    client_id=_broker.client_id,
    transport=_broker.transport,
)

if _broker.transport == "websockets":
    _mqtt_client.ws_set_options(path=_broker.ws_path)

_mqtt_client.username_pw_set(_broker.username, _broker.password)


def get_mqtt_client() -> mqtt.Client:
    return _mqtt_client


MqttClientDep = Annotated[mqtt.Client, Depends(get_mqtt_client)]
