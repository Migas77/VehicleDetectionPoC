import logging
from ipaddress import IPv4Address

from app.interfaces.location import LocationInterface
from app.schemas.camara.device import Device, DeviceIpv4Addr
from app.schemas.camara.location import Location, RetrievalLocationRequest
from app.schemas.poc.ue import UE
from app.settings import settings

LOG = logging.getLogger(__name__)


class CamaraLocationBackend(LocationInterface):
    """Retrieves UE location via the CAMARA Location Retrieval API."""

    def __init__(self) -> None:
        self._client = settings.create_camara_client()

    @staticmethod
    def _build_device(ue: UE) -> Device:
        if ue.msisdn is not None:
            phone = ue.msisdn if ue.msisdn.startswith("+") else f"+{ue.msisdn}"
            return Device(phoneNumber=phone)
        if ue.ip_address_v4 is not None:
            ip = IPv4Address(ue.ip_address_v4)
            return Device(
                ipv4Address=DeviceIpv4Addr(
                    publicAddress=ip,
                    privateAddress=ip,
                )
            )
        raise ValueError(
            f"Cannot identify device for UE supi={ue.supi}: "
            "neither ip_address_v4 nor msisdn is set"
        )

    async def retrieve_location(self, ue: UE) -> Location:
        payload = RetrievalLocationRequest(device=self._build_device(ue))
        LOG.info("Retrieving CAMARA location for UE supi=%s", ue.supi)
        res = await self._client.post(
            "/location-retrieval/v0.4/retrieve",
            content=payload.model_dump_json(exclude_unset=True),
            headers={"Content-Type": "application/json"},
        )
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA location retrieval failed ({res.status_code}): {res.text}"
            )
        location = Location.model_validate_json(res.content)
        LOG.info(
            "CAMARA location retrieved for UE supi=%s: areaType=%s",
            ue.supi,
            location.area.areaType,
        )
        return location
