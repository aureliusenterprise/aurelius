import importlib
from typing import List, Optional, Tuple
from unittest.mock import Mock

import pytest
import requests
from flask import Flask
from m4i_backend_core.auth import requires_auth
from m4i_backend_core.auth.model import AuthError


requires_auth_module = importlib.import_module("m4i_backend_core.auth.requires_auth")


@pytest.fixture
def app() -> Flask:
    return Flask(__name__)


def _protected_endpoint() -> Mock:
    return Mock(side_effect=lambda *, access_token: access_token)


def _configure_auth_mocks(
    monkeypatch: pytest.MonkeyPatch,
    *,
    kid: str,
    jwks_side_effect: List[object],
    decode_result: Optional[object] = None,
) -> Tuple[Mock, Mock, Mock, Mock]:
    jwks_mock = Mock(side_effect=jwks_side_effect)
    jwks_mock.cache_clear = Mock()

    openid_configuration_mock = Mock(
        return_value={"jwks_uri": "https://issuer.example/jwks"}
    )
    openid_configuration_mock.cache_clear = Mock()

    get_token_mock = Mock(return_value="token")
    decode_mock = Mock(return_value=decode_result or {"sub": "user-1"})

    monkeypatch.setattr(requires_auth_module, "jwks", jwks_mock)
    monkeypatch.setattr(
        requires_auth_module,
        "openid_configuration",
        openid_configuration_mock,
    )
    monkeypatch.setattr(requires_auth_module, "get_token_auth_header", get_token_mock)
    monkeypatch.setattr(
        requires_auth_module.jwt,
        "get_unverified_header",
        Mock(return_value={"alg": "RS256", "kid": kid}),
    )
    monkeypatch.setattr(requires_auth_module.jwt, "decode", decode_mock)

    return jwks_mock, openid_configuration_mock, get_token_mock, decode_mock


def test__retries_once_on_kid_miss_and_succeeds(
    app: Flask,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old_key = object()
    new_key = object()
    payload = {"sub": "rotated-user"}

    jwks_mock, openid_configuration_mock, _, decode_mock = _configure_auth_mocks(
        monkeypatch,
        kid="new-kid",
        jwks_side_effect=[
            {"old-kid": old_key},
            {"new-kid": new_key},
        ],
        decode_result=payload,
    )

    protected = requires_auth()(_protected_endpoint())

    with app.test_request_context():
        result = protected()

        assert result == "token"
        assert requires_auth_module._request_ctx_stack.top.current_user == payload

    jwks_mock.cache_clear.assert_called_once_with()
    openid_configuration_mock.cache_clear.assert_called_once_with()
    decode_mock.assert_called_once()
    assert decode_mock.call_args.kwargs["key"] is new_key


def test__raises_auth_error_when_kid_still_missing_after_retry(
    app: Flask,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jwks_mock, openid_configuration_mock, _, decode_mock = _configure_auth_mocks(
        monkeypatch,
        kid="missing-kid",
        jwks_side_effect=[
            {"old-kid": object()},
            {"other-kid": object()},
        ],
    )

    protected = requires_auth()(_protected_endpoint())

    with app.test_request_context(), pytest.raises(AuthError) as exc_info:
        protected()

    assert exc_info.value.status_code == 401
    assert jwks_mock.cache_clear.call_count == 2
    assert openid_configuration_mock.cache_clear.call_count == 2
    decode_mock.assert_not_called()


def test__maps_jwks_fetch_exception_to_500_auth_error(
    app: Flask,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jwks_mock = Mock(side_effect=requests.RequestException("jwks down"))
    jwks_mock.cache_clear = Mock()

    monkeypatch.setattr(requires_auth_module, "jwks", jwks_mock)
    monkeypatch.setattr(
        requires_auth_module, "get_token_auth_header", Mock(return_value="token")
    )
    monkeypatch.setattr(
        requires_auth_module.jwt,
        "get_unverified_header",
        Mock(return_value={"alg": "RS256", "kid": "kid-1"}),
    )

    decode_mock = Mock()
    monkeypatch.setattr(requires_auth_module.jwt, "decode", decode_mock)

    protected = requires_auth()(_protected_endpoint())

    with app.test_request_context(), pytest.raises(AuthError) as exc_info:
        protected()

    assert exc_info.value.status_code == 500
    decode_mock.assert_not_called()
