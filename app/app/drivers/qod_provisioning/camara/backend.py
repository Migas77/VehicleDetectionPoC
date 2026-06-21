import logging
from ipaddress import IPv4Address
from typing import Any

from pydantic import TypeAdapter

from app.interfaces.qod_provisioning import QoDProvisioningInterface
from app.schemas.camara.device import Device, DeviceIpv4Addr
from app.schemas.camara.qodProvisioning import (
    ProvisioningInfo,
    RetrieveProvisioningByDevice,
    TriggerProvisioning,
)
from app.schemas.poc import UE
from app.schemas.poc.ue_with_qos import UeWithQoS
from app.settings import settings

LOG = logging.getLogger(__name__)

_dict_adapter: TypeAdapter[dict[str, Any]] = TypeAdapter(dict[str, Any])


class CamaraQoDProvisioningBackend(QoDProvisioningInterface):
    """Creates and manages an indefinite QoD provisioning in the CAMARA gateway for a camera UE."""

    def __init__(self) -> None:
        self._client = settings.create_camara_client()
        self._notification_url = settings.camara_notification_url

    @staticmethod
    def _build_device(ue: UE) -> Device:
        if ue.ip_address_v4 is not None:
            ip = IPv4Address(ue.ip_address_v4)
            return Device(
                ipv4Address=DeviceIpv4Addr(
                    publicAddress=ip,
                    privateAddress=ip,
                )
            )
        if ue.msisdn is not None:
            phone = ue.msisdn if ue.msisdn.startswith("+") else f"+{ue.msisdn}"
            return Device(phoneNumber=phone)
        raise ValueError(
            f"Cannot identify device for UE id={ue.id}: "
            "neither ip_address_v4 nor msisdn is set"
        )

    async def assign_qos_profile(self, ue: UeWithQoS) -> str:
        sink = f"{self._notification_url}/callbacks/qod-provisioning/camara/{ue.id}"
        payload = TriggerProvisioning(
            device=self._build_device(ue),
            qosProfile=ue.qos_profile.qos_profile_name,
            sink=sink,
        )
        LOG.info(
            "Creating CAMARA QoD provisioning for UE id=%s, qosProfile=%s",
            ue.id,
            ue.qos_profile.qos_profile_name,
        )
        res = await self._client.post(
            "/qod-provisioning/v0.2/device-qos",
            content=payload.model_dump_json(exclude_unset=True),
            headers={"Content-Type": "application/json"},
        )
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA QoD provisioning failed ({res.status_code}): {res.text}"
            )
        provisioning = ProvisioningInfo.model_validate_json(res.content)
        LOG.info(
            "CAMARA QoD provisioning created for UE id=%s, provisioningId=%s",
            ue.id,
            provisioning.provisioningId,
        )
        return str(provisioning.provisioningId)

    async def get_qod_provisioning(self, provisioning_id: str) -> dict[str, Any]:
        res = await self._client.get(
            f"/qod-provisioning/v0.2/device-qos/{provisioning_id}"
        )
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA QoD get provisioning failed ({res.status_code}): {res.text}"
            )
        return _dict_adapter.validate_json(res.content)

    async def delete_qod_provisioning(self, provisioning_id: str) -> bool:
        LOG.info("Deleting CAMARA QoD provisioning id=%s", provisioning_id)
        res = await self._client.delete(
            f"/qod-provisioning/v0.2/device-qos/{provisioning_id}"
        )
        if res.status_code == 404:
            LOG.warning(
                "CAMARA QoD provisioning id=%s not found for deletion", provisioning_id
            )
            return False
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA QoD delete provisioning failed ({res.status_code}): {res.text}"
            )
        LOG.info("CAMARA QoD provisioning id=%s deleted", provisioning_id)
        return True

    async def retrieve_qod_provisioning_by_device(self, ue: UE) -> str | None:
        payload = RetrieveProvisioningByDevice(device=self._build_device(ue))
        res = await self._client.post(
            "/qod-provisioning/v0.2/retrieve-device-qos",
            content=payload.model_dump_json(exclude_unset=True),
            headers={"Content-Type": "application/json"},
        )
        if res.status_code == 404:
            return None
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA QoD retrieve by device failed ({res.status_code}): {res.text}"
            )
        provisioning = ProvisioningInfo.model_validate_json(res.content)
        return str(provisioning.provisioningId)
