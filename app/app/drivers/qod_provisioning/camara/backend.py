import logging
import time
from functools import cached_property
from ipaddress import IPv4Address
from typing import Any

import httpx
from pydantic import TypeAdapter

from app.drivers.capif_auth import discover_camara_url
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
        super().__init__()
        self._notification_url = settings.camara_notification_url

    @cached_property
    def _client(self) -> httpx.AsyncClient:
        return settings.create_camara_client()

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
            f"Cannot identify device for UE supi={ue.supi}: "
            "neither ip_address_v4 nor msisdn is set"
        )

    async def _create_provisioning(self, ue: UeWithQoS) -> str:
        sink = f"{self._notification_url}/callbacks/qod-provisioning/camara/{ue.supi}"
        payload = TriggerProvisioning(
            device=self._build_device(ue),
            qosProfile=ue.qos_profile.qos_profile_name,
            sink=sink,
        )
        # LOG.info(
        #     "Creating CAMARA QoD provisioning for UE supi=%s, qosProfile=%s",
        #     ue.supi,
        #     ue.qos_profile.qos_profile_name,
        # )
        url = discover_camara_url(
            fallback="/qod-provisioning/v0.2/device-qos",
            resource_name="Create Provisioning",
            api_name_filter="qod-provisioning",
            operation="POST",
        )
        body = payload.model_dump_json(exclude_unset=True)
        # await asyncio.sleep(8)  # benchmark: measure from a cold http connection
        _bench_start_ns = time.perf_counter_ns()
        res = await self._client.post(
            url,
            content=body,
            headers={"Content-Type": "application/json"},
        )
        _bench_elapsed_ns = time.perf_counter_ns() - _bench_start_ns
        LOG.info(
            'BENCHMARK: {"api": "CAMARA", "resource": "Create Provisioning", '
            '"filter": "qod-provisioning", "op": "POST", '
            '"x_correlator": "%s", "ue": "%s", "time_ns": %d, "status": %d}',
            res.request.headers.get("x-correlator") or "",
            ue.supi,
            _bench_elapsed_ns,
            res.status_code,
        )
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA QoD provisioning failed ({res.status_code}): {res.text}"
            )
        provisioning = ProvisioningInfo.model_validate_json(res.content)
        # LOG.info(
        #     "CAMARA QoD provisioning created for UE supi=%s, provisioningId=%s",
        #     ue.supi,
        #     provisioning.provisioningId,
        # )
        return str(provisioning.provisioningId)

    async def _replace_provisioning(self, provisioning_id: str, ue: UeWithQoS) -> str:
        """DELETE the provisioning and create a new one, as QoD Provisioning has no update.

        Deleting reverts the UE's QoS, so if the new profile is rejected no profile
        remains applied.
        """
        await self.delete_qod_provisioning(provisioning_id)
        await self.clear_qos_state(ue.supi)
        return await self.assign_qos_profile(ue)

    async def get_qod_provisioning(self, provisioning_id: str) -> dict[str, Any]:
        res = await self._client.get(
            discover_camara_url(
                fallback="/qod-provisioning/v0.2/device-qos/{provisioningId}",
                resource_name="Get Qod Information By Id",
                api_name_filter="qod-provisioning",
                operation="GET",
            ).format(provisioningId=provisioning_id)
        )
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA QoD get provisioning failed ({res.status_code}): {res.text}"
            )
        return _dict_adapter.validate_json(res.content)

    async def delete_qod_provisioning(self, provisioning_id: str) -> bool:
        # LOG.info("Deleting CAMARA QoD provisioning id=%s", provisioning_id)
        res = await self._client.delete(
            discover_camara_url(
                fallback="/qod-provisioning/v0.2/device-qos/{provisioningId}",
                resource_name="Delete Qod",
                api_name_filter="qod-provisioning",
                operation="DELETE",
            ).format(provisioningId=provisioning_id)
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
        # LOG.info("CAMARA QoD provisioning id=%s deleted", provisioning_id)
        return True

    async def retrieve_qod_provisioning_by_device(self, ue: UE) -> str | None:
        payload = RetrieveProvisioningByDevice(device=self._build_device(ue))
        res = await self._client.post(
            discover_camara_url(
                fallback="/qod-provisioning/v0.2/retrieve-device-qos",
                resource_name="Get Qod Information By Id",
                api_name_filter="qod-provisioning",
                operation="POST",
            ),
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
