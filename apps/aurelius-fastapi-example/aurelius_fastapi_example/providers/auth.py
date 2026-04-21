from functools import cache
from typing import Annotated, cast

import httpx
import jwt
from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jwt.algorithms import RSAAlgorithm
from pydantic import BaseModel, HttpUrl

from aurelius_fastapi_example.globals import LOGGER

from .http import http_client
from .settings import Settings


class OpenIdConfig(BaseModel):
    """OpenID configuration settings."""

    jwks_uri: HttpUrl

    class Config:
        """Model configuration."""

        frozen = True


@cache
def auth_base_url(*, settings: Settings) -> str:
    """Return the base URL for the authentication server."""
    return f"{settings.auth_server_url}realms/{settings.auth_realm_name}"


@cache
def auth_provider(*, auth_base_url: Annotated[str, Depends(auth_base_url)]) -> OAuth2PasswordBearer:
    """Return the OAuth2PasswordBearer instance for the authentication configuration."""
    return OAuth2PasswordBearer(
        tokenUrl=f"{auth_base_url}/protocol/openid-connect/token",
        description="Bearer token for authentication with the data source.",
    )


@cached(
    cache=TTLCache(maxsize=1, ttl=3600),
    key=lambda **kwargs: hashkey(kwargs["auth_base_url"]),
)
def openid_configuration(
    auth_base_url: Annotated[str, Depends(auth_base_url)],
    http_client: Annotated[httpx.Client, Depends(http_client)],
) -> OpenIdConfig:
    """Return the OpenID configuration for the configured issuer."""
    well_known_url = f"{auth_base_url}/.well-known/openid-configuration"

    response = http_client.get(well_known_url)
    response.raise_for_status()

    LOGGER.info("Loaded OpenID configuration from %s", well_known_url)

    return OpenIdConfig.model_validate_json(response.read())


@cached(
    cache=TTLCache(maxsize=1, ttl=3600),
    key=lambda **kwargs: hashkey(kwargs["openid"]),
)
def jwks(
    http_client: Annotated[httpx.Client, Depends(http_client)],
    openid: Annotated[OpenIdConfig, Depends(openid_configuration)],
) -> dict[str, RSAPublicKey]:
    """Return the JWKS configuration for the JWT authentication."""
    response = http_client.get(str(openid.jwks_uri))
    response.raise_for_status()

    response_json = response.json()

    result = {key["kid"]: cast("RSAPublicKey", RSAAlgorithm.from_jwk(key)) for key in response_json["keys"]}

    LOGGER.info("Loaded JWKS configuration from %s", openid.jwks_uri)

    return result


async def auth_token(
    auth_provider: Annotated[OAuth2PasswordBearer, Depends(auth_provider)],
    request: Request,
) -> str:
    """Return the authentication token from the request."""
    token = await auth_provider(request)

    if token is None:
        LOGGER.error("No authentication token provided")
        raise HTTPException(status_code=401, detail="Missing authorization token")

    return token


def jwk(
    auth_token: Annotated[str, Depends(auth_token)],
    jwks: Annotated[dict[str, RSAPublicKey], Depends(jwks)],
) -> RSAPublicKey:
    """Return the JWK key for decoding the authentication token."""
    try:
        headers = jwt.get_unverified_header(auth_token)
    except jwt.PyJWTError as e:
        LOGGER.exception("Failed to decode authentication token header")
        raise HTTPException(status_code=401, detail="Invalid authorization token format") from e

    if not (kid := headers.get("kid")):
        LOGGER.error("No key ID found in authentication token")
        raise HTTPException(status_code=401, detail="Missing key ID in token")

    if not (key := jwks.get(kid)):
        LOGGER.error("No key found for key ID %s", kid)
        raise HTTPException(status_code=401, detail="Authentication key not available")

    return key


def user_info(
    auth_base_url: Annotated[str, Depends(auth_base_url)],
    auth_token: Annotated[str, Depends(auth_token)],
    jwk: Annotated[RSAPublicKey, Depends(jwk)],
) -> dict:
    """Decode the authentication token to verify the user's identity and return their information."""
    try:
        headers = jwt.get_unverified_header(auth_token)  # NOSONAR(S5659) token is verified a few lines down
        alg = headers.get("alg", "RS256")

        if alg != "RS256":
            LOGGER.error("Unsupported JWT algorithm: %s", alg)
            raise HTTPException(status_code=401, detail="Unsupported token algorithm")

        return jwt.decode(
            auth_token,
            key=jwk,
            algorithms=[alg],
            issuer=auth_base_url,
            options={"verify_aud": False},
        )
    except jwt.ExpiredSignatureError as e:
        LOGGER.warning("Authentication token has expired")
        raise HTTPException(status_code=401, detail="Token has expired") from e
    except jwt.InvalidIssuerError as e:
        LOGGER.warning("Invalid token issuer")
        raise HTTPException(status_code=401, detail="Invalid token issuer") from e
    except jwt.PyJWTError as e:
        LOGGER.exception("Failed to verify authentication token")
        raise HTTPException(status_code=401, detail="Invalid authorization token") from e
