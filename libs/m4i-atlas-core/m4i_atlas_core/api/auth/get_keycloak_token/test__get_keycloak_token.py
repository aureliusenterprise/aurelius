from .get_keycloak_token import get_keycloak_token


def test__get_keycloak_token():
    access_token = get_keycloak_token()
    assert access_token is not None
# END test__get_keycloak_token
