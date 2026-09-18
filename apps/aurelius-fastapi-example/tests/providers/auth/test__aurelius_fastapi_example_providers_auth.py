import httpx
import jwt
import pytest
from aurelius_fastapi_example.models import Settings
from aurelius_fastapi_example.providers import auth
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pybreaker import CircuitBreaker


def build_credentials(token: str) -> HTTPAuthorizationCredentials:
    """Create an HTTPAuthorizationCredentials object with the given bearer token."""
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def test__auth_base_url_builds_realm_url(auth_base_url: str, auth_settings: Settings) -> None:
    """Auth base URL provider should compose the expected realm URL."""
    assert auth.auth_base_url(settings=auth_settings) == auth_base_url


def test__openid_configuration_loads_from_keycloak(
    auth_base_url: str,
    http_client: httpx.Client,
    auth_circuit_breaker: CircuitBreaker,
) -> None:
    """OpenID configuration provider should fetch well-known config from Keycloak."""
    config = auth.openid_configuration(
        auth_base_url=auth_base_url,
        http_client=http_client,
        auth_circuit_breaker=auth_circuit_breaker,
    )

    assert str(config.jwks_uri).endswith("/protocol/openid-connect/certs")


def test__jwks_loads_keys_from_keycloak(
    auth_base_url: str,
    http_client: httpx.Client,
    auth_circuit_breaker: CircuitBreaker,
) -> None:
    """JWKS provider should return at least one public key from Keycloak."""
    openid = auth.openid_configuration(
        auth_base_url=auth_base_url,
        http_client=http_client,
        auth_circuit_breaker=auth_circuit_breaker,
    )
    keys = auth.jwks(http_client=http_client, openid=openid, auth_circuit_breaker=auth_circuit_breaker)

    assert keys


def test__auth_token_extracts_bearer_token(keycloak_access_token: str) -> None:
    """Auth token provider should return the bearer token from credentials."""
    credentials = build_credentials(keycloak_access_token)

    token = auth.auth_token(credentials)

    assert token == keycloak_access_token


def test__jwk_selects_key_by_token_header(
    auth_base_url: str,
    keycloak_access_token: str,
    http_client: httpx.Client,
    auth_circuit_breaker: CircuitBreaker,
) -> None:
    """JWK provider should resolve the token's kid to a public key from the JWKS."""
    openid = auth.openid_configuration(
        auth_base_url=auth_base_url,
        http_client=http_client,
        auth_circuit_breaker=auth_circuit_breaker,
    )
    keys = auth.jwks(http_client=http_client, openid=openid, auth_circuit_breaker=auth_circuit_breaker)

    key = auth.jwk(keycloak_access_token, keys)

    assert key is not None


def test__user_info_decodes_valid_token(
    auth_base_url: str,
    keycloak_access_token: str,
    http_client: httpx.Client,
    auth_circuit_breaker: CircuitBreaker,
) -> None:
    """User info provider should decode and validate a valid Keycloak token."""
    openid = auth.openid_configuration(
        auth_base_url=auth_base_url,
        http_client=http_client,
        auth_circuit_breaker=auth_circuit_breaker,
    )
    keys = auth.jwks(http_client=http_client, openid=openid, auth_circuit_breaker=auth_circuit_breaker)

    key = auth.jwk(keycloak_access_token, keys)
    claims = auth.user_info(auth_base_url, keycloak_access_token, key)

    assert claims["iss"] == auth_base_url
    assert claims["azp"] == "admin-cli"


def test__user_info_rejects_wrong_issuer(
    auth_base_url: str,
    keycloak_access_token: str,
    http_client: httpx.Client,
    auth_circuit_breaker: CircuitBreaker,
) -> None:
    """User info provider should reject tokens when issuer does not match configured realm."""
    openid = auth.openid_configuration(
        auth_base_url=auth_base_url,
        http_client=http_client,
        auth_circuit_breaker=auth_circuit_breaker,
    )
    keys = auth.jwks(http_client=http_client, openid=openid, auth_circuit_breaker=auth_circuit_breaker)

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


def test__auth_circuit_breaker_configuration(auth_settings: Settings) -> None:
    """Circuit breaker should be configured with settings values."""
    cb = auth.auth_circuit_breaker(settings=auth_settings)

    assert cb.name == "auth_circuit_breaker"
    assert cb.fail_max == 5
    assert cb.reset_timeout == 60.0


def test__openid_configuration_returns_503_when_circuit_open(
    auth_base_url: str,
    http_client: httpx.Client,
) -> None:
    """OpenID configuration should return 503 when circuit breaker is open."""
    cb = CircuitBreaker(fail_max=1, reset_timeout=60.0)
    cb.open()

    with pytest.raises(
        HTTPException,
        check=lambda e: e.status_code == 503,
        match="temporarily unavailable",
    ):
        auth.openid_configuration(
            auth_base_url=auth_base_url,
            http_client=http_client,
            auth_circuit_breaker=cb,
        )


def test__jwks_returns_503_when_circuit_open(
    http_client: httpx.Client,
) -> None:
    """JWKS should return 503 when circuit breaker is open."""
    cb = CircuitBreaker(fail_max=1, reset_timeout=60.0)
    cb.open()

    with pytest.raises(
        HTTPException,
        check=lambda e: e.status_code == 503,
        match="temporarily unavailable",
    ):
        auth.jwks(
            http_client=http_client,
            openid=None,  # type: ignore[arg-type]
            auth_circuit_breaker=cb,
        )
