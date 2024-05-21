from typing import Awaitable, Callable, Optional, TypeVar

from aiohttp import BasicAuth, ClientResponse, ClientSession
from aiohttp.client import _RequestContextManager

from ...config import ConfigStore

RequestFactory = Callable[[str, ClientSession], _RequestContextManager]

R = TypeVar('R')

ResponseParser = Callable[[ClientResponse], Awaitable[R]]


config = ConfigStore.get_instance()


async def handle_request(
    path: str,
    request_factory: RequestFactory,
    response_parser: ResponseParser[R],
    access_token: Optional[str] = None
) -> R:

    atlas_url, username, password = config.get_many(
        "atlas.server.url",
        "atlas.credentials.username",
        "atlas.credentials.password"
    )

    url = f"{atlas_url}/{path}"

    auth = None
    headers: dict = {}

    access_token = access_token if access_token != '' else None

    if access_token is None:
        auth = BasicAuth(username, password)
    else:
        headers = {
            **headers,
            'Authorization': f'bearer {access_token}'
        }
    # END IF

    async with ClientSession(auth=auth, headers=headers) as session:

        async with request_factory(url, session) as response:

            response.raise_for_status()

            return await response_parser(response)
        # END response
    # END session

# END handle_request
