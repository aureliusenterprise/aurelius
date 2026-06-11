from typing import Any, Optional

from keycloak import KeycloakOpenID

import m4i_analytics.m4i.auth.config as config


class _Auth:
    _instance: Optional["_Auth"] = None

    def __init__(self) -> None:
        keycloak_config: dict[str, str] = config.KEYCLOAK_JSON
        self._keycloak_client: KeycloakOpenID = KeycloakOpenID(
            server_url=keycloak_config["auth-server-url"],
            realm_name=keycloak_config["realm"],
            client_id=keycloak_config["resource"],
        )

    # END __init__

    def get_access_token(
        self, username: Optional[str], password: Optional[str], totp: Optional[Any] = None
    ) -> Optional[str]:
        if username is None or password is None:
            raise ValueError("Username and password are required")
        token_response: dict[str, Any] = self._keycloak_client.token(  # type: ignore[reportGeneralTypeIssues]
            username, password, "password"
        )
        access_token: Optional[str] = token_response.get("access_token")
        return access_token

    # END get_token

    def get_well_know(self) -> Any:
        return self._keycloak_client.well_know()

    # END get_well_know


# END _Auth


def Auth() -> _Auth:
    """
    Factory function for the Auth instance
    :return: The Auth singleton instance
    """

    if _Auth._instance is None:
        _Auth._instance = _Auth()
    return _Auth._instance


# END Auth
