import logging

import jwt

from app.capif.invoker import capif_invoker

LOG = logging.getLogger(__name__)


def get_capif_token(force_refresh: bool = False) -> str:
    """
    Get the CAPIF access token needed to invoke the service APIs
    (NEF or CAMARA) published to CAPIF by their provider.
    """
    service_discoverer = capif_invoker.service_discoverer
    if not service_discoverer:
        raise RuntimeError(
            "Internal error: no service discoverer => no CAPIF token found"
        )

    token = service_discoverer.token
    if not force_refresh and token:
        try:
            jwt.decode(token, options={"verify_signature": False, "verify_exp": True})
            return str(service_discoverer.token)
        except jwt.ExpiredSignatureError:
            LOG.warning("CAPIF token is expired, requesting a new one")
        except jwt.InvalidTokenError:
            raise RuntimeError("Internal error: invalid CAPIF token")
        except jwt.PyJWTError:
            raise RuntimeError("Internal error: invalid CAPIF token (unknown error)")

    service_discoverer.get_tokens()
    return str(service_discoverer.token)
