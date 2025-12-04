class AuthError(Exception):

    """
    `AuthError` represents an authentication exception along with its associated status code.
    It is used internally by the `core.auth` package.
    The `auth` blueprint provides a default handler for these exceptions.

    :param error: The original error
    :type error: Exception
    :param status_code: The status code which should be returned to the user
    :type status_code: int
    """

    error: Exception
    status_code: int

    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code
    # END __init__
# END AuthError
