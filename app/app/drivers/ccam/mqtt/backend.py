import logging
import time
from functools import cached_property

import aiomqtt
import redis.asyncio as aioredis

from app.interfaces.ccam import CcamInterface
from app.mqtt import get_mqtt_client
from app.redis import get_redis
from app.schemas.ccam import (
    DENMActionId,
    DENMAltitude,
    DENMCcAndScc,
    DENMEventPosition,
    DENMEventType,
    DENMHeader,
    DENMManagementContainer,
    DENMMessage,
    DENMMessageInner,
    DENMPositionConfidenceEllipse,
    DENMSituationContainer,
)
from app.schemas.poc.crash_status import CrashLocation
from app.settings import settings

LOG = logging.getLogger(__name__)


class MqttCcamBackend(CcamInterface):
    """Publishes DENM messages to nearby vehicles over MQTT."""

    _SEQ_KEY = "poc:ccam:denm_seq"

    def __init__(self) -> None:
        self._redis: aioredis.Redis = get_redis()

    @cached_property
    def _client(self) -> aiomqtt.Client:
        return get_mqtt_client()

    @staticmethod
    def _its_timestamp() -> int:
        # ITS timestamp: seconds since Unix epoch minus seconds before 2004, plus leap seconds
        return int((time.time() - 1072915200) + 5)

    async def send_denm(self, location: CrashLocation) -> None:
        station_id = settings.ccam_broker.station_id
        topic = f"{settings.ccam_broker.topic_base_path}/{station_id}/DENM"
        ts = self._its_timestamp()
        lat = int(location.latitude * 10_000_000)
        lon = int(location.longitude * 10_000_000)
        message = DENMMessage(
            header=DENMHeader(
                protocolVersion=2,
                messageId=1,
                stationId=station_id,
            ),
            denm=DENMMessageInner(
                management=DENMManagementContainer(
                    actionId=DENMActionId(
                        originatingStationId=station_id,
                        sequenceNumber=int(await self._redis.incr(self._SEQ_KEY)),
                    ),
                    detectionTime=ts,
                    referenceTime=ts,
                    eventPosition=DENMEventPosition(
                        latitude=lat,
                        longitude=lon,
                        positionConfidenceEllipse=DENMPositionConfidenceEllipse(
                            semiMajorConfidence=0,
                            semiMinorConfidence=0,
                            semiMajorOrientation=0,
                        ),
                        altitude=DENMAltitude(
                            altitudeValue=18,
                            altitudeConfidence="unavailable",
                        ),
                    ),
                    relevanceDistance="lessThan500m",
                    validityDuration=settings.ccam_broker.validity_duration,
                    transmissionInterval=2000,
                    stationType=5,
                ),
                situation=DENMSituationContainer(
                    informationQuality=0,
                    eventType=DENMEventType(
                        ccAndScc=DENMCcAndScc(accident2=0),
                    ),
                ),
            ),
        )
        payload = message.model_dump_json()
        LOG.info(
            "Publishing DENM to topic=%s: (%d,%d)",
            topic,
            lat,
            lon,
        )
        await self._client.publish(topic, payload, qos=1)
