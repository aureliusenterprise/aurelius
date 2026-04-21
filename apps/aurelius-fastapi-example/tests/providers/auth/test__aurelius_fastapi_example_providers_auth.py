import httpx
import jwt
import pytest
from aurelius_fastapi_example.models import Settings
from aurelius_fastapi_example.providers import auth
from fastapi import HTTPException, Request


def build_request_with_bearer(token: str) -> Request:
    """Create a minimal ASGI request object carrying an Authorization header."""
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": [(b"authorization", f"Bearer {token}".encode())],
        "client": ("127.0.0.1", 12345),
        "server": ("127.0.0.1", 80),
    }

    return Request(scope)


def test__auth_base_url_builds_realm_url(auth_base_url: str, auth_settings: Settings) -> None:
    """Auth base URL provider should compose the expected realm URL."""
    assert auth.auth_base_url(settings=auth_settings) == auth_base_url


def test__openid_configuration_loads_from_keycloak(auth_base_url: str, http_client: httpx.Client) -> None:
    """OpenID configuration provider should fetch well-known config from Keycloak."""
    config = auth.openid_configuration(
        auth_base_url=auth_base_url,
        http_client=http_client,
    )

    assert str(config.jwks_uri).endswith("/protocol/openid-connect/certs")


def test__jwks_loads_keys_from_keycloak(auth_base_url: str, http_client: httpx.Client) -> None:
    """JWKS provider should return at least one public key from Keycloak."""
    openid = auth.openid_configuration(auth_base_url=auth_base_url, http_client=http_client)
    keys = auth.jwks(http_client=http_client, openid=openid)

    assert keys


async def test__auth_token_extracts_bearer_token(keycloak_access_token: str) -> None:
    """Auth token provider should return the bearer token from request headers."""
    oauth2 = auth.auth_provider(auth_base_url="http://issuer.example/realms/test")
    request = build_request_with_bearer(keycloak_access_token)

    token = await auth.auth_token(oauth2, request)

    assert token == keycloak_access_token


def test__jwk_selects_key_by_token_header(
    auth_base_url: str,
    keycloak_access_token: str,
    http_client: httpx.Client,
) -> None:
    """JWK provider should resolve the token's kid to a public key from the JWKS."""
    openid = auth.openid_configuration(auth_base_url=auth_base_url, http_client=http_client)
    keys = auth.jwks(http_client=http_client, openid=openid)

    key = auth.jwk(keycloak_access_token, keys)

    assert key is not None


def test__user_info_decodes_valid_token(
    auth_base_url: str,
    keycloak_access_token: str,
    http_client: httpx.Client,
) -> None:
    """User info provider should decode and validate a valid Keycloak token."""
    openid = auth.openid_configuration(auth_base_url=auth_base_url, http_client=http_client)
    keys = auth.jwks(http_client=http_client, openid=openid)

    key = auth.jwk(keycloak_access_token, keys)
    claims = auth.user_info(auth_base_url, keycloak_access_token, key)

    assert claims["iss"] == auth_base_url
    assert claims["azp"] == "admin-cli"


def test__user_info_rejects_wrong_issuer(
    auth_base_url: str,
    keycloak_access_token: str,
    http_client: httpx.Client,
) -> None:
    """User info provider should reject tokens when issuer does not match configured realm."""
    openid = auth.openid_configuration(auth_base_url=auth_base_url, http_client=http_client)
    keys = auth.jwks(http_client=http_client, openid=openid)

    key = auth.jwk(keycloak_access_token, keys)

    with pytest.raises(HTTPException, match="Invalid token issuer"):
        auth.user_info(f"{auth_base_url}/wrong", keycloak_access_token, key)


def test__jwk_rejects_unknown_key_id() -> None:
    """JWK provider should raise 401 when token kid is missing from provided JWKS map."""
    token = jwt.encode(
        {"sub": "test-sub"},
        key="test-secret",
        algorithm="HS256",
        headers={"kid": "missing-key"},
    )

    with pytest.raises(HTTPException, match="Authentication key not available"):
        auth.jwk(token, {})
