import urllib.parse
from enum import Enum

import requests
from requests_toolbelt import MultipartEncoder

from m4i_analytics.m4i.auth.Auth import Auth


class ContentType(Enum):
    """
    This class enumerates various content types. Use these values to
    specify what kind of result you expect from your request.
    """

    TEXT = "text"
    JSON = "json"
    BINARY = "binary"
    RAW = "raw"

    @classmethod
    def is_valid(cls, value):
        """
        Check whether the provided value matches with one of the defined
        content types

        :returns: bool: whether or not the provided value is a defined
            content type

        :param any value: The value you want to check against the defined
            content types
        """

        return isinstance(value, ContentType) or any(value == item.value for item in cls)

    # END is_valid


# END ContentType


class ApiUtils:
    """
    This class provides various utility functions for API classes that
    connect with Models4Insight.
    """

    _ERR_URL_NOT_DEFINED = "Request URL is not defined"
    _ERR_URL_NOT_VALID = "Request URL is not valid"
    _ERR_CT_NOT_DEFINED = "Content type is not defined"
    _ERR_CT_NOT_VALID = "Content type is not valid"

    @staticmethod
    def get(
        url,
        params=None,
        content_type=ContentType.TEXT,
        proxies=None,
        use_default_proxies=True,
        username=None,
        password=None,
        totp=None,
        access_token=None,
    ):
        """
        Make a HTTP GET request with the given parameters to the given url.
        Specify what kind of result you expect by providing the content type.

        :returns: The response of the server, parsed to the specified content
            type (TEXT by default).

        :param str url: The url to which the request will be made.
        :param dict params: *Optional*. The parameters to provide with the
            request. By default, no parameters will be provided.
        :param ContentType content_type: *Optional*. The type of result you
            are expecting. By default, the content type is set to TEXT.
        :param proxies: *Optional*. Add http proxy information to allow
            writing data while being behind a proxy.
        :param use_default_proxies *Optional*. Proxies can be set in the
            operating system and might be available to python.
            With this option you can deliberately disable proxy settings
            in the environment.

        :exception TypeError: Thrown when the url, params and/or content
            type are not defined.
        :exception ValueError: Thrown when the url, params and/or content
            type are not valid.
        :exception requests.exceptions.HTTPError: Thrown when the request
            returned with a 400/500 code variant.
        """

        if params is None:
            params = {}
        if proxies is None:
            proxies = {}

        if url is None:
            raise TypeError(ApiUtils._ERR_URL_NOT_DEFINED)
        elif not isinstance(url, str):
            raise ValueError(ApiUtils._ERR_URL_NOT_VALID)
        elif content_type is None:
            raise TypeError(ApiUtils._ERR_CT_NOT_DEFINED)
        elif not ContentType.is_valid(content_type):
            raise ValueError(ApiUtils._ERR_CT_NOT_VALID)

        if isinstance(content_type, ContentType):
            content_type = content_type.value

        # Create the session and set the proxies.
        s = requests.Session()
        if access_token is not None or (username is not None and password is not None):
            s = ApiUtils._authorize(s, username, password, totp, access_token)

        if proxies:
            s.proxies = proxies
        if not use_default_proxies:
            s.trust_env = False
        params_encoded = urllib.parse.urlencode(
            {key: value for key, value in params.items() if value is not None},
            quote_via=urllib.parse.quote,
        )
        return ApiUtils._handle_response(s.get(url, params=params_encoded), content_type)

    # END get

    @staticmethod
    def post(
        url,
        data=None,
        file=None,
        content_type=ContentType.TEXT,
        proxies=None,
        use_default_proxies=True,
        username=None,
        password=None,
        totp=None,
        access_token=None,
    ):
        """
        Make a HTTP POST request with the given data to the given url.
        Specify what kind of result you expect by providing the content type.

        :returns: The response of the server, parsed to the specified content
            type (TEXT by default).

        :param str url: The url to which the request will be made
        :param dict data: *Optional*. The data to provide with the request.
            By default, no data will be provided.
        :param ContentType content_type: *Optional*. The type of result you
            are expecting. By default, the content type is set to TEXT.
        :param proxies: *Optional*. Add http proxy information to allow
            writing data while being behind a proxy.
        :param use_default_proxies *Optional*. Proxies can be set in the
            operating system and might be available to python.
            With this option you can deliberately disable proxy settings
            in the environment.

        :exception TypeError: Thrown when the url, data and/or content
            type are not defined
        :exception ValueError: Thrown when the url, data and/or content
            type are not valid
        :exception requests.exceptions.HTTPError: Thrown when the request
            returned with a 400/500 code variant
        """

        if data is None:
            data = {}
        if proxies is None:
            proxies = {}

        if url is None:
            raise TypeError(ApiUtils._ERR_URL_NOT_DEFINED)
        elif not isinstance(url, str):
            raise ValueError(ApiUtils._ERR_URL_NOT_VALID)
        elif content_type is None:
            raise TypeError(ApiUtils._ERR_CT_NOT_DEFINED)
        elif not ContentType.is_valid(content_type):
            raise ValueError(ApiUtils._ERR_CT_NOT_VALID)

        if isinstance(content_type, ContentType):
            content_type = content_type.value

        if file is not None:
            data["file"] = (file.name, file, "application/octet-stream")
            data = MultipartEncoder(fields=data)

        # Create the session and set the proxies.
        s = requests.Session()
        if access_token is not None or (username is not None and password is not None):
            s = ApiUtils._authorize(s, username, password, totp, access_token)

        if proxies:
            s.proxies = proxies
        if not use_default_proxies:
            s.trust_env = False

        request = s.post(url, data=data)

        return ApiUtils._handle_response(request, content_type)

    # END post

    @staticmethod
    def post_file(
        url,
        data=None,
        file=None,
        content_type=ContentType.TEXT,
        proxies=None,
        use_default_proxies=True,
        username=None,
        password=None,
        totp=None,
        access_token=None,
    ):
        """
        Make a HTTP POST request with the given data to the given url.
        Specify what kind of result you expect by providing the content type.

        :returns: The response of the server, parsed to the specified content
            type (TEXT by default).

        :param str url: The url to which the request will be made
        :param dict data: *Optional*. The data to provide with the request.
            By default, no data will be provided.
        :param ContentType content_type: *Optional*. The type of result you
            are expecting. By default, the content type is set to TEXT.
        :param proxies: *Optional*. Add http proxy information to allow
            writing data while being behind a proxy.
        :param use_default_proxies *Optional*. Proxies can be set in the
            operating system and might be available to python.
            With this option you can deliberately disable proxy settings
            in the environment.

        :exception TypeError: Thrown when the url, data and/or content
            type are not defined
        :exception ValueError: Thrown when the url, data and/or content
            type are not valid
        :exception requests.exceptions.HTTPError: Thrown when the request
            returned with a 400/500 code variant
        """

        if proxies is None:
            proxies = {}
        if data is None:
            data = {}
        if url is None:
            raise TypeError(ApiUtils._ERR_URL_NOT_DEFINED)
        elif not isinstance(url, str):
            raise ValueError(ApiUtils._ERR_URL_NOT_VALID)
        elif data is None:
            raise TypeError("Data is not defined")
        elif not isinstance(data, dict):
            raise ValueError("Data is not valid")
        elif content_type is None:
            raise TypeError(ApiUtils._ERR_CT_NOT_DEFINED)
        elif not ContentType.is_valid(content_type):
            raise ValueError(ApiUtils._ERR_CT_NOT_VALID)
        elif file is None:
            raise TypeError("File is not defined")

        if isinstance(content_type, ContentType):
            content_type = content_type.value

        # Create the session and set the proxies.
        s = requests.Session()
        if access_token is not None or (username is not None and password is not None):
            s = ApiUtils._authorize(s, username, password, totp, access_token)

        if proxies:
            s.proxies = proxies
        if not use_default_proxies:
            s.trust_env = False

        request = s.post(url, files={"file": (file.name, file)}, data=data)

        return ApiUtils._handle_response(request, content_type)

    # END post_file

    @staticmethod
    def post_json(
        url,
        data=None,
        file=None,
        content_type=ContentType.TEXT,
        proxies=None,
        use_default_proxies=True,
        username=None,
        password=None,
        totp=None,
        access_token=None,
    ):
        """
        Make a HTTP POST request with the given data to the given url.
        Specify what kind of result you expect by providing the content type.

        :returns: The response of the server, parsed to the specified content
            type (TEXT by default).

        :param str url: The url to which the request will be made
        :param dict data: *Optional*. The data to provide with the request.
            By default, no data will be provided.
        :param ContentType content_type: *Optional*. The type of result you
            are expecting. By default, the content type is set to TEXT.
        :param proxies: *Optional*. Add http proxy information to allow
            writing data while being behind a proxy.
        :param use_default_proxies *Optional*. Proxies can be set in the
            operating system and might be available to python.
            With this option you can deliberately disable proxy settings
            in the environment.

        :exception TypeError: Thrown when the url, data and/or content
            type are not defined
        :exception ValueError: Thrown when the url, data and/or content
            type are not valid
        :exception requests.exceptions.HTTPError: Thrown when the request
            returned with a 400/500 code variant
        """

        if proxies is None:
            proxies = {}
        if data is None:
            data = {}
        if url is None:
            raise TypeError(ApiUtils._ERR_URL_NOT_DEFINED)
        elif not isinstance(url, str):
            raise ValueError(ApiUtils._ERR_URL_NOT_VALID)
        elif data is None:
            raise TypeError("Data is not defined")
        elif not isinstance(data, dict):
            raise ValueError("Data is not valid")
        elif content_type is None:
            raise TypeError(ApiUtils._ERR_CT_NOT_DEFINED)
        elif not ContentType.is_valid(content_type):
            raise ValueError(ApiUtils._ERR_CT_NOT_VALID)

        if isinstance(content_type, ContentType):
            content_type = content_type.value
        # Create the session and set the proxies.
        s = requests.Session()
        if access_token is not None or (username is not None and password is not None):
            s = ApiUtils._authorize(s, username, password, totp, access_token)

        if proxies:
            s.proxies = proxies
        if not use_default_proxies:
            s.trust_env = False

        request = s.post(url, json=data)

        return ApiUtils._handle_response(request, content_type)

    # END post

    @staticmethod
    def delete(
        url,
        params=None,
        content_type=ContentType.TEXT,
        proxies=None,
        use_default_proxies=True,
        username=None,
        password=None,
        totp=None,
        access_token=None,
    ):
        """
        Make a HTTP DELETE request with the given parameters to the given url.
        Specify what kind of result you expect by providing the content type.

        :returns: The response of the server, parsed to the specified content
            type (TEXT by default).

        :param str url: The url to which the request will be made.
        :param dict params: *Optional*. The parameters to provide with the
            request. By default, no parameters will be provided.
        :param ContentType content_type: *Optional*. The type of result you
            are expecting. By default, the content type is set to TEXT.
        :param proxies: *Optional*. Add http proxy information to allow
            writing data while being behind a proxy.
        :param use_default_proxies *Optional*. Proxies can be set in the
            operating system and might be available to python.
            With this option you can deliberately disable proxy settings
            in the environment.

        :exception TypeError: Thrown when the url, params and/or content
            type are not defined.
        :exception ValueError: Thrown when the url, params and/or content
            type are not valid.
        :exception requests.exceptions.HTTPError: Thrown when the request
            returned with a 400/500 code variant.
        """

        if proxies is None:
            proxies = {}
        if params is None:
            params = {}
        if url is None:
            raise TypeError(ApiUtils._ERR_URL_NOT_DEFINED)
        elif not isinstance(url, str):
            raise ValueError(ApiUtils._ERR_URL_NOT_VALID)
        elif params is None:
            raise TypeError("Params is not defined")
        elif not isinstance(params, dict):
            raise ValueError("Params is not valid")
        elif content_type is None:
            raise TypeError(ApiUtils._ERR_CT_NOT_DEFINED)
        elif not ContentType.is_valid(content_type):
            raise ValueError(ApiUtils._ERR_CT_NOT_VALID)

        if isinstance(content_type, ContentType):
            content_type = content_type.value

        # Create the session and set the proxies.
        s = requests.Session()
        if access_token is not None or (username is not None and password is not None):
            s = ApiUtils._authorize(s, username, password, totp, access_token)

        if proxies:
            s.proxies = proxies
        if not use_default_proxies:
            s.trust_env = False
        params_encoded = urllib.parse.urlencode(
            {key: value for key, value in params.items() if value is not None},
            quote_via=urllib.parse.quote,
        )
        return ApiUtils._handle_response(s.delete(url, params=params_encoded), content_type)

    # END delete

    @staticmethod
    def _authorize(session, username, password, totp=None, access_token=None):
        authorization_header = "Bearer %s" % (
            access_token if access_token else Auth().get_access_token(username, password, totp)
        )
        session.headers.update({"Authorization": authorization_header})
        return session

    # END _authorize

    @staticmethod
    def _handle_response(response, content_type):
        if response is None:
            raise TypeError("HTTP response is not defined")
        elif not isinstance(response, requests.Response):
            raise ValueError("HTTP response is not valid")
        elif content_type is None:
            raise TypeError("Content type is not defined")
        elif not ContentType.is_valid(content_type):
            raise ValueError("Content type is not valid")
        # print(response.text)
        # Raises an exception if the response code is a 400/500 code
        response.raise_for_status()

        result = None

        if content_type == ContentType.TEXT.value:
            result = response.text

        if content_type == ContentType.JSON.value:
            result = response.json()

        if content_type == ContentType.BINARY.value:
            result = response.content

        if content_type == ContentType.RAW.value:
            result = response.raw.read(10)

        return result

    # END _handle_response


# END ApiUtils
