import logging
from typing import Generator, Optional

import httpx

LOG = logging.getLogger(__name__)


class NEFJwtAuth(httpx.Auth):
    """httpx Auth handler that acquires and caches a NEF bearer token via username/password."""

    requires_response_body = True

    def __init__(self, nef_url: str, username: str, password: str) -> None:
        self._nef_url = nef_url.rstrip("/")
        self._username = username
        self._password = password
        self._current_token: Optional[str] = None

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        token = self._current_token
        if token is None:
            res = yield self._build_login_request()
            token = self._update_token(res)
        request.headers["Authorization"] = token
        res = yield request
        if res.status_code == 401:
            res = yield self._build_login_request()
            token = self._update_token(res)
            request.headers["Authorization"] = token
            yield request

    def _build_login_request(self) -> httpx.Request:
        LOG.debug("Fetching NEF auth token")
        return httpx.Request(
            method="POST",
            url=f"{self._nef_url}/api/v1/login/access-token",
            data={"username": self._username, "password": self._password},
        )

    def _update_token(self, res: httpx.Response) -> str:
        if not res.is_success:
            LOG.error("NEF login failed (%s): %s", res.status_code, res.text)
            raise RuntimeError("Failed to authenticate with NEF emulator")
        token = f"Bearer {res.json()['access_token']}"
        self._current_token = token
        return token
