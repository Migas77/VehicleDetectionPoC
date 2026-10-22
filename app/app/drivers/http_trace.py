import json
import logging
import time
from typing import Any

LOG = logging.getLogger(__name__)


class HttpPhaseTracer:
    """
    Collects httpcore's `trace` extension timestamps for a single outbound httpx
    request and logs a DELAY breakdown of the phases the underlying TCP/TLS/HTTP
    exchange goes through.

    Usage:
        tracer = HttpPhaseTracer()
        res = await client.post(url, ..., extensions={"trace": tracer.trace})
        tracer.log("my.op", x_correlator=x_correlator)

    Phases (each becomes a `<phase>_ms` field when the underlying event fired):
      - dns_and_tcp_connect_ms: `connect_tcp` span. httpcore resolves the host
        (DNS) and opens the TCP socket in the same call, so this number is the
        two combined and cannot be split further without patching the resolver.
      - tls_handshake_ms: `start_tls` span (only fires for https:// requests).
      - send_request_headers_ms / send_request_body_ms: time spent writing the
        request onto the socket.
      - ttfb_ms: `receive_response_headers` span — time to first byte, i.e. how
        long the peer took to start responding once the request was sent.
      - receive_response_body_ms: time spent reading/streaming the response body.

    When the connection is reused from the pool (keep-alive), `connect_tcp` and
    `start_tls` never fire, so those fields are omitted and `connection_reused`
    is set to true instead.
    """

    def __init__(self) -> None:
        self._t: dict[str, int] = {}

    async def trace(self, name: str, info: dict[str, Any]) -> None:
        self._t[name] = time.perf_counter_ns()

    def _span_ms(self, started: str, complete: str) -> float | None:
        t0 = self._t.get(started)
        t1 = self._t.get(complete)
        if t0 is None or t1 is None:
            return None
        return round((t1 - t0) / 1e6, 3)

    def log(self, op: str, **extra: Any) -> None:
        fields: dict[str, Any] = dict(extra)

        connect_ms = self._span_ms(
            "connection.connect_tcp.started", "connection.connect_tcp.complete"
        )
        fields["connection_reused"] = connect_ms is None
        if connect_ms is not None:
            fields["dns_and_tcp_connect_ms"] = connect_ms

        tls_ms = self._span_ms(
            "connection.start_tls.started", "connection.start_tls.complete"
        )
        if tls_ms is not None:
            fields["tls_handshake_ms"] = tls_ms

        send_headers_ms = self._span_ms(
            "http11.send_request_headers.started",
            "http11.send_request_headers.complete",
        )
        if send_headers_ms is not None:
            fields["send_request_headers_ms"] = send_headers_ms

        send_body_ms = self._span_ms(
            "http11.send_request_body.started", "http11.send_request_body.complete"
        )
        if send_body_ms is not None:
            fields["send_request_body_ms"] = send_body_ms

        ttfb_ms = self._span_ms(
            "http11.receive_response_headers.started",
            "http11.receive_response_headers.complete",
        )
        if ttfb_ms is not None:
            fields["ttfb_ms"] = ttfb_ms

        body_ms = self._span_ms(
            "http11.receive_response_body.started",
            "http11.receive_response_body.complete",
        )
        if body_ms is not None:
            fields["receive_response_body_ms"] = body_ms

        LOG.info("DELAY: %s", json.dumps({"op": op, **fields}))
