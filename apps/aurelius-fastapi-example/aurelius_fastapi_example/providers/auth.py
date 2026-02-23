from functools import cache
from typing import Annotated

import httpx
import jwt
import jwt.algorithms
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, HttpUrl

from aurelius_fastapi_example.globals import LOGGER, SETTINGS

auth_base_url = f"{SETTINGS.auth_server_url}realms/{SETTINGS.auth_realm_name}"

auth = OAuth2PasswordBearer(
    tokenUrl=f"{auth_base_url}/protocol/openid-connect/token",
    description="Bearer token for authentication with the data source.",
)


class OpenIdConfig(BaseModel):
    """OpenID configuration settings."""

    jwks_uri: HttpUrl

    class Config:
        """Model configuration."""

        frozen = True


@cache
def openid_configuration() -> OpenIdConfig:
    """Return the OpenID configuration for the configured issuer."""
    well_known_url = f"{auth_base_url}/.well-known/openid-configuration"

    response = httpx.get(well_known_url)
    response.raise_for_status()

    LOGGER.info("Loaded OpenID configuration from %s", well_known_url)

    return OpenIdConfig.model_validate_json(response.read())


@cache
def jwks(openid: Annotated[OpenIdConfig, Depends(openid_configuration)]) -> dict:
    """Return the JWKS configuration for the JWT authentication."""
    response = httpx.get(str(openid.jwks_uri))

    response.raise_for_status()
    response_json = response.json()

    result = {key["kid"]: jwt.algorithms.RSAAlgorithm.from_jwk(key) for key in response_json["keys"]}

    LOGGER.info("Loaded JWKS configuration from %s", openid.jwks_uri)

    return result


def user_info(
    jwks: Annotated[dict, Depends(jwks)],
    token: Annotated[str, Depends(auth)],
) -> dict:
    """Decode the JWT token using the JWT authentication configuration."""
    try:
        headers = jwt.get_unverified_header(token)

        if not (kid := headers.get("kid")):
            LOGGER.error("No key ID found in JWT token")
            raise HTTPException(status_code=401)

        if not (key := jwks.get(kid)):
            LOGGER.error("No key found for key ID %s", kid)
            raise HTTPException(status_code=401)

        LOGGER.debug("Decoding JWT token with key %s", kid)

        return jwt.decode(
            token,
            key=key,
            algorithms=["RS256"],
            issuer=auth_base_url,
            options={"verify_aud": False},
        )
    except jwt.PyJWTError as e:
        LOGGER.exception("Failed to verify JWT")
        raise HTTPException(status_code=401) from e
