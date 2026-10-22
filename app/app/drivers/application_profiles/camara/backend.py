import logging
import time
from functools import cached_property

import httpx

from app.utilities import bitrate_str_to_rate
from app.drivers.capif_auth import discover_camara_url
from app.interfaces.application_profiles import ApplicationProfilesInterface
from app.schemas.camara.application_profiles import (
    ApplicationProfile,
    ApplicationProfileId,
    ApplicationProfileRequest,
    NetworkQualityThresholds,
)
from app.schemas.poc.ue_with_qos import UeWithQoS
from app.settings import settings

LOG = logging.getLogger(__name__)


class CamaraApplicationProfilesBackend(ApplicationProfilesInterface):
    """Creates and retrieves ApplicationProfiles via the CAMARA Application Profiles API."""

    @cached_property
    def _client(self) -> httpx.AsyncClient:
        return settings.create_camara_client()

    async def create_application_profile(self, ue: UeWithQoS) -> ApplicationProfile:
        requirements = settings.cameras.get_stream_requirements_by_ue_supi(ue.supi)
        if requirements is None:
            LOG.warning(
                "UE supi=%s not found in camera settings, using default", ue.supi
            )
            requirements = settings.cameras.default_stream_requirements
        payload = ApplicationProfileRequest(
            networkQualityThresholds=NetworkQualityThresholds(
                targetMinUpstreamRate=bitrate_str_to_rate(requirements.min_ul_bitrate),
                targetMinDownstreamRate=bitrate_str_to_rate(
                    requirements.min_dl_bitrate
                ),
            ),
        )
        # LOG.info("Creating CAMARA ApplicationProfile for UE supi=%s", ue.supi)
        url = discover_camara_url(
            fallback="/application-profiles/v0.5/application-profiles",
            resource_name="Create Application Profile",
            api_name_filter="application-profiles",
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
            'BENCHMARK: {"api": "CAMARA", "resource": "Create Application Profile", '
            '"filter": "application-profiles", "op": "POST", '
            '"x_correlator": "%s", "ue": "%s", "time_ns": %d, "status": %d}',
            res.request.headers.get("x-correlator") or "",
            ue.supi,
            _bench_elapsed_ns,
            res.status_code,
        )
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA ApplicationProfile creation failed ({res.status_code}): {res.text}"
            )
        profile = ApplicationProfile.model_validate_json(res.content)
        # LOG.info(
        #     "CAMARA ApplicationProfile created for UE supi=%s, id=%s",
        #     ue.supi,
        #     profile.applicationProfileId,
        # )
        return profile

    async def get_application_profile(
        self,
        ue_supi: str,
        application_profile_id: ApplicationProfileId | None = None,
    ) -> ApplicationProfile:
        if application_profile_id is None:
            raise RuntimeError(
                f"CAMARA ApplicationProfile get requires application_profile_id for UE supi={ue_supi}"
            )
        res = await self._client.get(
            discover_camara_url(
                fallback="/application-profiles/v0.5/application-profiles/{applicationProfileId}",
                resource_name="Get Application Profile By Id",
                api_name_filter="application-profiles",
                operation="GET",
            ).format(applicationProfileId=application_profile_id)
        )
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA ApplicationProfile get failed ({res.status_code}): {res.text}"
            )
        return ApplicationProfile.model_validate_json(res.content)

    async def delete_application_profile(
        self, application_profile_id: ApplicationProfileId
    ) -> bool:
        # LOG.info("Deleting CAMARA ApplicationProfile id=%s", application_profile_id)
        res = await self._client.delete(
            discover_camara_url(
                fallback="/application-profiles/v0.5/application-profiles/{applicationProfileId}",
                resource_name="Delete Application Profile By Id",
                api_name_filter="application-profiles",
                operation="DELETE",
            ).format(applicationProfileId=application_profile_id)
        )
        if res.status_code == 404:
            LOG.warning(
                "CAMARA ApplicationProfile id=%s not found for deletion",
                application_profile_id,
            )
            return False
        if not res.is_success:
            raise RuntimeError(
                f"CAMARA ApplicationProfile delete failed ({res.status_code}): {res.text}"
            )
        # LOG.info("CAMARA ApplicationProfile id=%s deleted", application_profile_id)
        return True
