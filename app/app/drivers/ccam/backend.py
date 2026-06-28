import logging
from functools import cached_property

import aiomqtt

from app.interfaces.ccam import CcamInterface
from app.mqtt import get_mqtt_client
from app.schemas.ccam import (
    DENMEventPosition,
    DENMManagementContainer,
    DENMMessage,
    DENMMessageInner,
    DENMSituationContainer,
    ReferencePositionWithConfidence,
)
from app.settings import settings

LOG = logging.getLogger(__name__)


class MqttCcamBackend(CcamInterface):
    """Publishes DENM messages to nearby vehicles over MQTT."""

    @cached_property
    def _client(self) -> aiomqtt.Client:
        return get_mqtt_client()

    async def send_denm(
        self, location: ReferencePositionWithConfidence, text: str
    ) -> None:
        # TODO: verify DENM topic structure and payload format with the actual broker/vehicles
        topic = f"{settings.ccam_broker.topic_base_path}/DENM"
        message = DENMMessage(
            denm=DENMMessageInner(
                managementContainer=DENMManagementContainer(
                    eventPosition=DENMEventPosition(
                        latitude=location.latitude,
                        longitude=location.longitude,
                    )
                ),
                situationContainer=DENMSituationContainer(freeText=text),
            )
        )
        payload = message.model_dump_json()
        LOG.info(
            "Publishing DENM to topic=%s: (%d,%d)",
            topic,
            location.latitude,
            location.longitude,
        )
        await self._client.publish(topic, payload)
