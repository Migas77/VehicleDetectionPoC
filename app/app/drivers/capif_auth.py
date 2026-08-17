import logging
from typing import Generator

import httpx

from app.capif import CAMARA_CAPIF_API_NAME, NEF_CAPIF_API_NAME
from app.capif.deps import get_capif_token
from app.capif.invoker import capif_invoker
from app.settings import settings

LOG = logging.getLogger(__name__)


class CAPIFAuth(httpx.Auth):
    """httpx Auth handler that signs requests with the CAPIF-issued access token."""

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = f"Bearer {get_capif_token()}"
        res = yield request

        if res.status_code == 401:
            request.headers["Authorization"] = (
                f"Bearer {get_capif_token(force_refresh=True)}"
            )
            yield request


def discover_url(
    *,
    api_name: str,
    fallback: str,
    resource_name: str,
    api_name_filter: str,
    operation: str,
) -> str:
    """
    fallback url will be the returned url if CAPIF is not being used
    otherwise, the url will be discovered via CAPIF using the provided resource name and api name filter
    if the url cannot be discovered via CAPIF, the fallback url will be returned and an error will be logged

    `api_name` is the name the provider published its service APIs under in CAPIF:
    NEF_CAPIF_API_NAME for the NEF, CAMARA_CAPIF_API_NAME for the GSMA Open Gateway.
    `resource_name` is the OpenAPI operation summary - neither provider sets one
    explicitly, so it is the FastAPI default derived from the endpoint function name
    (create_subscription -> "Create Subscription", post_subscriptions -> "Post Subscriptions").
    """
    if settings.net_apis.auth_mode != "capif":
        return fallback

    path = capif_invoker.get_service_relative_url(
        api_name=api_name,
        resource_name=resource_name,
        api_name_filter=api_name_filter,
        operation=operation,
    )
    if path is None:
        LOG.error(
            "Path not found for resource '%s', api filter '%s', operation '%s'. Falling back to fallback url.",
            resource_name,
            api_name_filter,
            operation,
        )
        return fallback
    return path


def discover_nef_url(
    *, fallback: str, resource_name: str, api_name_filter: str, operation: str
) -> str:
    """discover_url bound to the service APIs published by the NEF."""
    return discover_url(
        api_name=NEF_CAPIF_API_NAME,
        fallback=fallback,
        resource_name=resource_name,
        api_name_filter=api_name_filter,
        operation=operation,
    )


def discover_camara_url(
    *, fallback: str, resource_name: str, api_name_filter: str, operation: str
) -> str:
    """discover_url bound to the service APIs published by the GSMA Open Gateway."""
    return discover_url(
        api_name=CAMARA_CAPIF_API_NAME,
        fallback=fallback,
        resource_name=resource_name,
        api_name_filter=api_name_filter,
        operation=operation,
    )
