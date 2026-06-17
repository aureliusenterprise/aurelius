import importlib
from unittest.mock import MagicMock, patch

from m4i_atlas_core.api.auth.get_keycloak_token.get_keycloak_token import get_keycloak_token


# Load the actual module file for patching the ConfigStore instance at module level
token_module = importlib.import_module("m4i_atlas_core.api.auth.get_keycloak_token.get_keycloak_token")


def test__get_keycloak_token():
    mock_config = MagicMock()
    mock_config.get_many.side_effect = [
        (
            "http://localhost:8180/auth",
            "atlas",
            "master",
            "secret",
        ),  # server_url, client_id, realm_name, client_secret_key
        ("admin", "password"),  # username, password
    ]

    mock_keycloak_class = MagicMock()
    mock_keycloak_instance = MagicMock()
    mock_keycloak_instance.token.return_value = {"access_token": "test-token"}
    mock_keycloak_class.return_value = mock_keycloak_instance

    with patch.object(token_module, "store", mock_config):
        with patch.object(token_module, "KeycloakOpenID", mock_keycloak_class):
            access_token = get_keycloak_token()
            assert access_token == "test-token"


# END test__get_keycloak_token


# END test__get_keycloak_token
