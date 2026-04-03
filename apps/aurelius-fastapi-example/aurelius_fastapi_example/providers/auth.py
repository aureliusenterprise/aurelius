from functools import cache
from typing import Annotated, cast

import httpx
import jwt
import jwt.algorithms
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, HttpUrl

from aurelius_fastapi_example.globals import LOGGER

from .settings import Settings


class OpenIdConfig(BaseModel):
    """OpenID configuration settings."""

    jwks_uri: HttpUrl

    class Config:
        """Model configuration."""

        frozen = True


@cache
def auth_base_url(settings: Settings) -> str:
    """Return the base URL for the authentication server."""
    return f"{settings.auth_server_url}realms/{settings.auth_realm_name}"


@cache
def auth_provider(auth_base_url: Annotated[str, Depends(auth_base_url)]) -> OAuth2PasswordBearer:
    """Return the OAuth2PasswordBearer instance for the authentication configuration."""
    return OAuth2PasswordBearer(
        tokenUrl=f"{auth_base_url}/protocol/openid-connect/token",
        description="Bearer token for authentication with the data source.",
    )


@cache
def openid_configuration(auth_base_url: Annotated[str, Depends(auth_base_url)]) -> OpenIdConfig:
    """Return the OpenID configuration for the configured issuer."""
    well_known_url = f"{auth_base_url}/.well-known/openid-configuration"

    response = httpx.get(well_known_url)
    response.raise_for_status()

    LOGGER.info("Loaded OpenID configuration from %s", well_known_url)

    return OpenIdConfig.model_validate_json(response.read())


@cache
def jwks(openid: Annotated[OpenIdConfig, Depends(openid_configuration)]) -> dict[str, jwt.algorithms.AllowedPublicKeys]:
    """Return the JWKS configuration for the JWT authentication."""
    response = httpx.get(str(openid.jwks_uri))

    response.raise_for_status()
    response_json = response.json()

    result = {
        key["kid"]: cast("jwt.algorithms.AllowedPublicKeys", jwt.algorithms.RSAAlgorithm.from_jwk(key))
        for key in response_json["keys"]
    }

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
        raise HTTPException(status_code=401)

    return token


def jwk(
    auth_token: Annotated[str, Depends(auth_token)],
    jwks: Annotated[dict[str, jwt.algorithms.AllowedPublicKeys], Depends(jwks)],
) -> jwt.algorithms.AllowedPublicKeys:
    """Return the JWK key for decoding the authentication token."""
    try:
        headers = jwt.get_unverified_header(auth_token)
    except jwt.PyJWTError as e:
        LOGGER.exception("Failed to decode authentication token header")
        raise HTTPException(status_code=401) from e

    if not (kid := headers.get("kid")):
        LOGGER.error("No key ID found in authentication token")
        raise HTTPException(status_code=401)

    if not (key := jwks.get(kid)):
        LOGGER.error("No key found for key ID %s", kid)
        raise HTTPException(status_code=401)

    return key


def user_info(
    auth_base_url: Annotated[str, Depends(auth_base_url)],
    auth_token: Annotated[str, Depends(auth_token)],
    jwk: Annotated[jwt.algorithms.AllowedPublicKeys, Depends(jwk)],
) -> dict:
    """Decode the authentication token to verify the user's identity and return their information."""
    try:
        return jwt.decode(
            auth_token,
            key=jwk,
            algorithms=["RS256"],
            issuer=auth_base_url,
            options={"verify_aud": False},
        )
    except jwt.PyJWTError as e:
        LOGGER.exception("Failed to verify authentication token")
        raise HTTPException(status_code=401) from e
