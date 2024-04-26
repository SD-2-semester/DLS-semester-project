from typing import Annotated, Any, AsyncGenerator

from aiohttp import ClientSession
from fastapi import Depends

from chat_service import exceptions


async def get_http_client() -> AsyncGenerator[ClientSession, None]:
    """Get aiohttp client."""

    async with ClientSession() as client:
        yield client


class HttpService:
    """Service for sending http requests."""

    def __init__(
        self,
        http_client: ClientSession = Depends(get_http_client),
    ) -> None:
        self.http_client = http_client

    async def get(
        self,
        url: str,
    ) -> dict[str, Any]:
        """Send get request to url."""

        try:
            response = await self.http_client.get(
                url,
            )
        except Exception as e:
            raise exceptions.Http500(
                f"Internal request failed for url: {url}",
            ) from e

        if response.status != 200:
            raise exceptions.Http500(
                f"Request failed with status {response.status} for url: {url}"
            )

        return await response.json()


GetHttpClient = Annotated[HttpService, Depends(HttpService)]
