from typing import Callable, Protocol

from m4i_backend_core.auth import requires_auth


class AuthProvider(Protocol):
    """Protocol for providing authentication decoration."""

    def requires_auth(self) -> Callable:
        """Return a decorator that enforces authentication."""
        ...


class KeycloakAuthProvider(AuthProvider):
    """Auth provider using Keycloak for JWT validation."""

    def requires_auth(self) -> Callable:
        """Return the real requires_auth decorator with JWT validation."""
        return requires_auth()
