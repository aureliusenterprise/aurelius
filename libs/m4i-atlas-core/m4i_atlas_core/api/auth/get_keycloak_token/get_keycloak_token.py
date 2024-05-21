from typing import Tuple

from keycloak import KeycloakOpenID

from ....config import ConfigStore

store = ConfigStore.get_instance()


def get_keycloak_token(keycloak: KeycloakOpenID | None = None, credentials: Tuple[str, str] | None = None, totp: str | None = None) -> str:
    """
    Retrieves an access token from the given Keycloak instance using the given username and password.

    Returns the access token.

    This function relies on the following configurations:

    | Key                             | Description                                                                                                                                                                                                                                                      |
    |---------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | "keycloak.server.url"           | The url of the Keycloak server. In case of a local connection, this includes the hostname and the port. E.g. `http://localhost:8180/auth`. In case of an external connection, provide a fully qualified domain name. E.g. `https://www.models4insight.com/auth`. |
    | "keycloak.client.id"            | The name of the Keycloak client.                                                                                                                                                                                                                                 |
    | "keycloak.realm.name"           | The name of the Keycloak realm.                                                                                                                                                                                                                                  |
    | "keycloak.client.secret.key"    | The public RS256 key associated with the Keycloak realm.                                                                                                                                                                                                         |
    | "keycloak.credentials.username" | The username of the Keycloak user.                                                                                                                                                                                                                               |
    | "keycloak.credentials.password" | The password of the Keycloak user.                                                                                                                                                                                                                               |

    :param keycloak KeycloakOpenID: Optional Keycloak instance. If none is given, creates one using pre-configured parameters. Default is `None`.
    :param credentials Tuple[str, str]: Optional username and password for authentication with Keycloak. If none are given, uses pre-configured credentials. Default is `None`.
    :param totp str: Optional one-time access token for multi-factor authenticaton. Default is `None`.

    :return: A valid access token
    :rtype: str
    """

    if keycloak is None:
        server_url, client_id, realm_name, client_secret_key = store.get_many(
            "keycloak.server.url",
            "keycloak.client.id",
            "keycloak.realm.name",
            "keycloak.client.secret.key",
            all_required=True
        )

        keycloak = KeycloakOpenID(
            server_url=server_url,
            client_id=client_id,
            realm_name=realm_name,
            client_secret_key=client_secret_key
        )
    # END IF

    if credentials is not None:
        username, password = credentials
    else:
        username, password = store.get_many(
            "keycloak.credentials.username",
            "keycloak.credentials.password",
            all_required=True
        )
    # END IF

    token = keycloak.token(
        username=username,
        password=password,
        totp=totp
    )

    return token['access_token']
# END get_keycloak_token
