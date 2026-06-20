import logging
from typing import Any, Optional

from pydantic import TypeAdapter

from app.interfaces.qos_profiles import QoSProfilesInterface
from app.schemas.nef.qosInformation import NefQosCharacteristics
from app.schemas.poc.ue_with_qos import UeWithQoS
from app.settings import settings

LOG = logging.getLogger(__name__)

_ProfileListAdapter: TypeAdapter[list[dict[str, Any]]] = TypeAdapter(
    list[dict[str, Any]]
)


class NefQoSProfilesBackend(QoSProfilesInterface):
    """Verifies a QoS profile exists in the NEF and if announced bitrates match the expected QosProfile."""

    def __init__(self) -> None:
        self._client = settings.create_nef_client()

    async def get_qos_profiles(
        self, ue: Optional[UeWithQoS] = None
    ) -> list[dict[str, Any]]:
        res = await self._client.get(
            "/api/v1/qosInfo/qosCharacteristics"
            f"{f'/{ue.qos_profile.qos_profile_name}' if ue and ue.qos_profile.qos_profile_name else ''}"
        )
        if not res.is_success:
            raise RuntimeError(
                f"Failed to fetch NEF QoS profiles ({res.status_code}): {res.text}"
            )
        return _ProfileListAdapter.validate_json(res.content)

    async def verify_qos_profile(self, ue: UeWithQoS) -> bool:
        name = ue.qos_profile.qos_profile_name
        LOG.info("Verifying NEF QoS profile '%s' for UE id=%s", name, ue.id)
        res = await self._client.get(f"/api/v1/qosInfo/qosCharacteristics/{name}")
        if res.status_code == 404:
            LOG.warning("NEF QoS profile '%s' not found", name)
            return False
        if not res.is_success:
            raise RuntimeError(
                f"Unexpected NEF response ({res.status_code}): {res.text}"
            )

        profile = NefQosCharacteristics.model_validate_json(res.content)
        nef_ul_bps = profile.uplinkBitRate  # bps integer, optional
        nef_dl_bps = profile.downlinkBitRate  # bps integer, optional

        if nef_ul_bps is None:
            LOG.warning(
                "NEF QoS profile '%s' uplinkBitRate is missing or invalid", name
            )
            return False
        if nef_dl_bps is None:
            LOG.warning(
                "NEF QoS profile '%s' downlinkBitRate is missing or invalid", name
            )
            return False

        expected_ul = ue.qos_profile.ul_bitrate_bps()
        expected_dl = ue.qos_profile.dl_bitrate_bps()

        if nef_ul_bps != expected_ul:
            LOG.warning(
                "NEF QoS profile '%s' ul_bitrate mismatch: expected %s bps, got %s bps",
                name,
                expected_ul,
                nef_ul_bps,
            )
            return False
        if nef_dl_bps != expected_dl:
            LOG.warning(
                "NEF QoS profile '%s' dl_bitrate mismatch: expected %s bps, got %s bps",
                name,
                expected_dl,
                nef_dl_bps,
            )
            return False

        LOG.info("NEF QoS profile '%s' verified", name)
        return True
