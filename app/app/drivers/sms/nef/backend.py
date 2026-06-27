import logging
from functools import cached_property

import httpx

from app.interfaces.sms import SMSInterface
from app.schemas.nef.sms import SMSSendRequest
from app.schemas.poc.ue import UE
from app.settings import settings

LOG = logging.getLogger(__name__)


class NefSMSBackend(SMSInterface):
    @cached_property
    def _client(self) -> httpx.AsyncClient:
        return settings.create_nef_auth_client()

    async def send_sms(self, ue: UE, text: str) -> None:
        if ue.msisdn is None:
            raise ValueError(
                f"UE id={ue.id} has no MSISDN configured — cannot send SMS"
            )

        payload = SMSSendRequest(gpsi=f"msisdn-{ue.msisdn}", text=text)
        res = await self._client.post(
            "/api/v1/sms/send",
            content=payload.model_dump_json(exclude_unset=True),
            headers={"Content-Type": "application/json"},
        )
        if not res.is_success:
            raise RuntimeError(f"NEF SMS send failed ({res.status_code}): {res.text}")

        LOG.info("SMS sent to UE id=%s msisdn=%s", ue.id, ue.msisdn)
