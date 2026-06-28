from app.drivers.ccam.mqtt.backend import MqttCcamBackend
from app.settings import settings

if settings.ccam_broker.backend != "mqtt":
    raise RuntimeError(
        "MqttCcamBackend instantiated but ccam_broker.backend isn't 'mqtt'"
    )

mqtt_ccam_interface = MqttCcamBackend()
