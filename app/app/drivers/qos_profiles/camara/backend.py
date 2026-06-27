import logging
from typing import Any, Optional

from pydantic import TypeAdapter

from app.drivers.utilities import rate_to_bps
from app.interfaces.qos_profiles import QoSProfilesInterface
from app.schemas.camara.qos_profiles import (
    QosProfile as CamaraQosProfile,
    QosProfileDeviceRequest,
)
from app.schemas.poc.ue_with_qos import UeWithQoS
from app.settings import settings

LOG = logging.getLogger(__name__)

_ProfileListAdapter: TypeAdapter[list[dict[str, Any]]] = TypeAdapter(
    list[dict[str, Any]]
)


class CamaraQoSProfilesBackend(QoSProfilesInterface):
    """Verifies a QoS profile exists in the CAMARA gateway and its bitrates match the expected QosProfile."""

    def __init__(self) -> None:
        self._client = settings.create_camara_client()

    async def get_qos_profiles(
        self, ue: Optional[UeWithQoS] = None
    ) -> list[dict[str, Any]]:
        res = await self._client.post(
            "/qos-profiles/v1/retrieve-qos-profiles",
            content=QosProfileDeviceRequest(
                name=ue.qos_profile.qos_profile_name
                if ue and ue.qos_profile.qos_profile_name
                else None
            ).model_dump_json(),
            headers={"Content-Type": "application/json"},
        )
        if not res.is_success:
            raise RuntimeError(
                f"Failed to fetch CAMARA QoS profiles ({res.status_code}): {res.text}"
            )
        return _ProfileListAdapter.validate_json(res.content)

    async def verify_qos_profile(self, ue: UeWithQoS) -> bool:
        name = ue.qos_profile.qos_profile_name
        LOG.info("Verifying CAMARA QoS profile '%s' for UE supi=%s", name, ue.supi)
        res = await self._client.get(f"/qos-profiles/v1/qos-profiles/{name}")
        if res.status_code == 404:
            LOG.warning("CAMARA QoS profile '%s' not found", name)
            return False
        if not res.is_success:
            raise RuntimeError(
                f"Unexpected CAMARA response ({res.status_code}): {res.text}"
            )

        profile = CamaraQosProfile.model_validate_json(res.content)
        camara_upstream_rate = profile.maxUpstreamRate
        camara_downstream_rate = profile.maxDownstreamRate

        if (
            camara_upstream_rate is None
            or camara_upstream_rate.value is None
            or camara_upstream_rate.unit is None
        ):
            LOG.warning(
                "CAMARA QoS profile '%s' maxUpstreamRate is missing or invalid", name
            )
            return False
        if (
            camara_downstream_rate is None
            or camara_downstream_rate.value is None
            or camara_downstream_rate.unit is None
        ):
            LOG.warning(
                "CAMARA QoS profile '%s' maxDownstreamRate is missing or invalid", name
            )
            return False

        camara_ul_bps = rate_to_bps(
            camara_upstream_rate.value, camara_upstream_rate.unit.value
        )
        camara_dl_bps = rate_to_bps(
            camara_downstream_rate.value, camara_downstream_rate.unit.value
        )
        expected_ul = ue.qos_profile.max_ul_bitrate_bps()
        expected_dl = ue.qos_profile.max_dl_bitrate_bps()

        if camara_ul_bps != expected_ul:
            LOG.warning(
                "CAMARA QoS profile '%s' maxUpstreamRate mismatch: expected %s bps, got %s bps",
                name,
                expected_ul,
                camara_ul_bps,
            )
            return False
        if camara_dl_bps != expected_dl:
            LOG.warning(
                "CAMARA QoS profile '%s' maxDownstreamRate mismatch: expected %s bps, got %s bps",
                name,
                expected_dl,
                camara_dl_bps,
            )
            return False

        LOG.info("CAMARA QoS profile '%s' verified", name)
        return True
