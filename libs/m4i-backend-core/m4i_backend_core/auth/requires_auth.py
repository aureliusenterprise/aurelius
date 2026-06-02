from functools import partial, wraps
from typing import Dict, cast

import jwt
import requests
from cachetools import TTLCache, cached
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from flask import _request_ctx_stack
from jwt.algorithms import RSAAlgorithm

from ..config import AUTH_ISSUER
from .get_token_auth_header import get_token_auth_header
from .model import AuthError


@cached(cache=TTLCache(maxsize=1, ttl=3600))
def openid_configuration() -> Dict:
    """Return the OpenID configuration for the configured issuer."""
    well_known_url = f"{AUTH_ISSUER}/.well-known/openid-configuration"

    response = requests.get(well_known_url, timeout=10)
    response.raise_for_status()

    return response.json()


@cached(cache=TTLCache(maxsize=1, ttl=3600))
def jwks() -> Dict[str, RSAPublicKey]:
    """Return the JWKS configuration for the JWT authentication."""
    openid = openid_configuration()

    response = requests.get(openid["jwks_uri"], timeout=10)
    response.raise_for_status()

    response_json = response.json()

    result = {
        key["kid"]: cast("RSAPublicKey", RSAAlgorithm.from_jwk(key))
        for key in response_json["keys"]
    }

    return result


def requires_auth(f=None, transparent: bool = False):
    """
    Provides a wrapper for functions which handle requests.
    Determines whether the access token provided with the request is valid.
    Passes the access token to the decorated function as a named parameter called `access_token`.

    When `transparent`, does not validate the token. This is useful when the token just needs to be passed on to another service.

    :exception AuthError: Thrown whenever the access token cannot be verified for any reason
    """

    if f is None:
        return partial(requires_auth, transparent=transparent)

    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()

        if transparent:
            return f(access_token=token, *args, **kwargs)

        try:
            headers = jwt.get_unverified_header(token)
            alg = headers.get("alg", "RS256")

            if alg != "RS256":
                raise AuthError(
                    {
                        "code": "invalid_algorithm",
                        "description": f"Unsupported signing algorithm: {alg}",
                    },
                    401,
                )

            kid = headers.get("kid")

            if not kid:
                raise AuthError(
                    {
                        "code": "invalid_header",
                        "description": "Authorization token is missing 'kid' header.",
                    },
                    401,
                )

            try:
                keys = jwks()
            except requests.RequestException:
                raise AuthError(
                    {
                        "code": "jwks_fetch_error",
                        "description": "Unable to fetch JWKS keys for token verification.",
                    },
                    500,
                )

            if kid not in keys:
                raise AuthError(
                    {
                        "code": "invalid_header",
                        "description": "Authorization token 'kid' header does not match any known keys.",
                    },
                    401,
                )

            payload = jwt.decode(
                token,
                key=keys[kid],
                algorithms=["RS256"],
                issuer=AUTH_ISSUER,
                options={"verify_aud": False},
            )

        except jwt.ExpiredSignatureError:
            raise AuthError(
                {
                    "code": "token_expired",
                    "description": "Token expired.",
                },
                401,
            )

        except jwt.InvalidIssuerError:
            raise AuthError(
                {
                    "code": "invalid_claims",
                    "description": "Incorrect claims. Please, check the issuer.",
                },
                401,
            )
        except jwt.InvalidSignatureError:
            raise AuthError(
                {
                    "code": "invalid_signature",
                    "description": "Signature verification failed.",
                },
                401,
            )
        except jwt.PyJWTError:
            raise AuthError(
                {
                    "code": "invalid_header",
                    "description": "Unable to parse authentication token.",
                },
                401,
            )

        _request_ctx_stack.top.current_user = payload

        return f(access_token=token, *args, **kwargs)

    return decorated
