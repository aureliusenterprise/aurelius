import logging
import traceback
from flask_restx import Api
from sqlalchemy.orm.exc import NoResultFound

from m4i_lineage_rest_api import settings

log = logging.getLogger(__name__)

api = Api(version='1.0', title='Lineage REST API',
          description='A simple demonstration of a Flask RestPlus powered API')


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500


@api.errorhandler(NoResultFound)
def database_not_found_error_handler(e):
    """No results found in database"""
    log.warning(traceback.format_exc())
    return {'message': 'A database result was required but none was found.'}, 404


"""
common response codes:
400 Bad Request – client sent an invalid request, such as lacking required request body or parameter
401 Unauthorized – client failed to authenticate with the server
403 Forbidden – client authenticated but does not have permission to access the requested resource
404 Not Found – the requested resource does not exist
412 Precondition Failed – one or more conditions in the request header fields evaluated to false
500 Internal Server Error – a generic error occurred on the server
503 Service Unavailable – the requested service is not available
"""
