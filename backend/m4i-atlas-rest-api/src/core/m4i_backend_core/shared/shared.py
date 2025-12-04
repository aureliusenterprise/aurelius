from flask import Flask, jsonify

from m4i_backend_core.auth import register as register_auth


def register(app: Flask):
    """
    Initializes the given application with core modules and routes.

    :param app: The application which should be initialized
    :type app: Flask
    """

    # Register the authentication module with the given app
    register_auth(app)

    @app.route('/heartbeat', methods=['GET'])
    def heartbeat():
        """
        This route can be called to check whether the application is still alive. It returns a simple json response.

        :return: A simple json response
        :rtype: str
        """
        return jsonify(success=True)
    # END heartbeat
# END register
