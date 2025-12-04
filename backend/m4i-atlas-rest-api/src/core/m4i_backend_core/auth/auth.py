from flask import Flask, jsonify
from .model import AuthError

def register(app: Flask):
    """
    Registers the authentication module with the given application. This includes error handling for authenticaton errors

    :param app: The application with which to register the auth module.
    :type app: Flask
    """

    @app.errorhandler(AuthError)
    def handle_auth_error(ex: AuthError) -> (str, int):
        """
        Error handler for exceptions related to authentication

        :param ex: The auth exception
        :type ex: AuthError

        :return: A HTTP Response mirroring the status code and message defined by the auth exception
        :rtype: (str, int)
        """

        response = jsonify(ex.error)
        return response, ex.status_code
    # END handle_auth_error
# END register
