import logging
import os
from typing import Any

import opencapif_sdk

from app.capif import CAPIF_SDK_CONFIG_PATH

LOG = logging.getLogger(__name__)


class CapifInvoker:
    def __init__(self, config_path: str) -> None:
        self.config_path: str = config_path
        self.invoker: opencapif_sdk.capif_invoker_connector | None = None
        self.service_discoverer: opencapif_sdk.service_discoverer | None = None

    def startup(self) -> None:
        LOG.info("Onboarding new invoker if not onboarded")
        self.invoker = opencapif_sdk.capif_invoker_connector(
            config_file=self.config_path
        )

        if not self.__is_onboarded():
            self.invoker.onboard_invoker()
            self.service_discoverer = opencapif_sdk.service_discoverer(
                config_file=self.config_path
            )
            api_invoker_id = self.service_discoverer.invoker_capif_details.get(
                "api_invoker_id"
            )
            LOG.info("New Invoker Onboarded with id %s", api_invoker_id)
        else:
            self.service_discoverer = opencapif_sdk.service_discoverer(
                config_file=self.config_path
            )

        self.service_discoverer.discover()
        self.service_discoverer.get_tokens()

    def shutdown(self) -> None:
        if not self.invoker:
            LOG.warning("Shutdown called but invoker was never initialized")
            return

        if not self.service_discoverer:
            LOG.warning(
                "Shutdown called but service discoverer is unavailable; skipping offboarding"
            )
            return

        api_invoker_id = self.service_discoverer.invoker_capif_details.get(
            "api_invoker_id"
        )
        LOG.info("Offboarding invoker with id %s", api_invoker_id)
        self.invoker.offboard_invoker()

    def __is_onboarded(self) -> bool:
        """
        The invoker is onboarded if the capif detail file exists, and you can successfully discover the service APIs
        """
        if self.invoker is None:
            return False

        try:
            capif_detils_path = os.path.join(
                self.invoker.invoker_folder, self.invoker.invoker_capif_details_filename
            )
            if not os.path.exists(capif_detils_path):
                LOG.info("Capif Details file not found. Invoker not onboarded")
                return False

            # The service discoverer loads the capif details file on construction, so it
            # can only be built once that file is known to exist - and it has to be built
            # here, otherwise this check can never succeed and every restart onboards a
            # brand new invoker instead of reusing the persisted one
            if self.service_discoverer is None:
                self.service_discoverer = opencapif_sdk.service_discoverer(
                    config_file=self.config_path
                )

            self.service_discoverer.discover()
            api_invoker_id = self.service_discoverer.invoker_capif_details.get(
                "api_invoker_id"
            )
            LOG.info("Invoker already onboarded (id=%s)", api_invoker_id)
            return True
        except Exception as e:
            LOG.warning(
                "Error during Service Discovery (for checking onboarding). %s; Invoker may not be onboarded yet.",
                e,
            )
            return False

    def _get_security_context(self, api_name: str) -> dict[str, Any]:
        """Return the discovered security context of the service API published as `api_name`.

        The PoC may find both the NEF ("api") and the GSMA Open Gateway
        ("gsma-open-gateway") published in the same CAPIF, so the context is picked by
        api name instead of always taking the first one.
        """
        if not self.service_discoverer:
            raise RuntimeError(
                "No service discoverer => no discovered service APIs. startup() must run first"
            )

        contexts: list[dict[str, Any]] = self.service_discoverer.invoker_capif_details[
            "registered_security_contexes"
        ]
        context = next((c for c in contexts if c.get("api_name") == api_name), None)
        if context is None:
            raise RuntimeError(
                f"No service API named '{api_name}' discovered in CAPIF "
                f"(discovered: {[c.get('api_name') for c in contexts]}). "
                "Make sure the provider has published its APIs to CAPIF."
            )
        return context

    def get_base_url(self, api_name: str) -> str:
        """
        Get the base URL (host + port) from the CAPIF security context.
        From https://192.168.0.180:443/nef/api/v1/3gpp-monitoring-event/v1/...
        Returns e.g. https://192.168.0.180:443

        Only the origin is returned (unlike the gateway, which appends the published base
        path) because the PoC drivers address the providers with the full published uri -
        /nef/api/v1/3gpp-monitoring-event/... for NEF, /geofencing-subscriptions/... for
        the CAMARA gateway - and the latter has no common base path to strip.
        """
        interface = self._get_security_context(api_name)["aef_profiles"][0][
            "interface_descriptions"
        ][0]
        port = interface["port"]

        if interface.get("ipv4_addr"):
            host = interface["ipv4_addr"]
        elif interface.get("fqdn"):
            host = interface["fqdn"]
        elif interface.get("ipv6_addr"):
            host = f"[{interface['ipv6_addr']}]"
        else:
            raise RuntimeError(
                f"Service API '{api_name}' has no ipv4Addr, ipv6Addr or fqdn "
                "in its AEF interface description"
            )

        return f"https://{host}:{port}"

    def get_service_relative_url(
        self,
        *,
        api_name: str,
        resource_name: str,
        api_name_filter: str,
        operation: str,
    ) -> str | None:
        """
        Get the relative URL (path) for a given resource name, optionally filtering by API name.
        From https://192.168.0.180:443/nef/api/v1/3gpp-monitoring-event/v1/...
        Returns e.g. /nef/api/v1/3gpp-monitoring-event/v1/...

        The published uri is returned as is (the gateway trims it up to the /3gpp- marker)
        because get_base_url only yields the origin here.
        """
        context = self._get_security_context(api_name)
        resources = context["aef_profiles"][0]["versions"][0]["resources"]

        matches = [
            r["uri"]
            for r in resources
            if r["resource_name"] == resource_name
            and api_name_filter in r["uri"]
            and operation in r["operations"]
        ]
        if not matches:
            LOG.warning(
                "No resource found with name '%s', filter '%s', operation '%s'",
                resource_name,
                api_name_filter,
                operation,
            )
            return None

        return str(matches[0])


capif_invoker = CapifInvoker(CAPIF_SDK_CONFIG_PATH)
