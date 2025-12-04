from functools import partial, wraps
from traceback import print_exc

from flask import _request_ctx_stack, session
from jose import jwt

from ..config import AUTH_ISSUER, AUTH_PUBLIC_KEY
from .get_token_auth_header import get_token_auth_header
from .model import AuthError


def requires_auth(f = None, transparent: bool = False):
    """
    Provides a wrapper for functions which handle requests.
    Determines whether the access token provided with the request is valid.
    Passes the access token to the decorated function as a named parameter called `access_token`.

    When `transparent`, does not validate the token. This is useful when the token just needs to be passed on to another service.

    :exception AuthError: Thrown whenever the access token cannot be verified for any reason
    """

    if f is None:
        return partial(requires_auth, transparent=transparent)
    # END IF

    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()

        if transparent:
            return f(access_token=token, *args, **kwargs)
        # END IF

        try:
            payload = jwt.decode(
                token,
                AUTH_PUBLIC_KEY,
                algorithms='RS256',
                issuer=AUTH_ISSUER,
                options={
                    'verify_aud': False
                }
            )

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the issuer.'
            }, 401)
        except jwt.JWTError:
            raise AuthError({
                'code': 'invalid_signature',
                'description': 'Signature verification failed.'
            }, 401)
        except Exception:
            print_exc()
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 401)

        _request_ctx_stack.top.current_user = payload

        return f(access_token=token, *args, **kwargs)
    # END decorated

    return decorated
# END requires_auth
