from fastapi import Depends, FastAPI, Request
from fastapi.security import HTTPBearer
from settings import settings
from httpx import AsyncClient
from typing import Any
from fastapi.responses import UJSONResponse
from typing import Annotated

app = FastAPI(
    title="Gateway",
    docs_url="/gateway/api/docs",
    redoc_url="/gateway/api/redoc",
    openapi_url="/gateway/api/openapi.json",
    default_response_class=UJSONResponse,
)

security = HTTPBearer()


async def authenticate_token(token: str, client: AsyncClient) -> dict[str, Any]:
    response = await client.get(
        f"{settings.auth_url}/auth/api/v1/users/me",
        headers={"Authorization": token},
    )
    return response.json()


async def get_http_client():
    async with AsyncClient() as client:
        yield client


HttpClient = Annotated[AsyncClient, Depends(get_http_client)]
Auth = Annotated[str, Depends(security)]


@app.post("/noauth/{service}/{path:path}")
async def route_post_request_noauth(
    service: str,
    path: str,
    client: HttpClient,
    body: dict[str, Any] | None = None,
):

    response = await client.post(
        f"{settings.auth_url}/{service}/{path}",
        json=body,
    )
    return response.json()


@app.get("/noauth/{service}/{path:path}")
async def route_get_request_noauth(
    service: str,
    path: str,
    request: Request,
    client: HttpClient,
):

    response = await client.get(
        f"{settings.get_service_url(service_name=service)}/{path}",
        params=request.query_params,
    )

    return response.json()


@app.post("/protected/{service}/{path:path}")
async def route_post_request(
    service: str,
    path: str,
    authorization: Auth,
    client: HttpClient,
    body: dict[str, Any] | None = None,
):
    token = authorization.credentials  # type: ignore
    await authenticate_token(token, client)

    response = await client.post(
        f"{settings.get_service_url(service_name=service)}/{path}",
        json=body,
        headers={"Authorization": token},
    )

    return response.json()


@app.get("/protected/{service}/{path:path}")
async def route_get_request(
    service: str,
    path: str,
    authorization: Auth,
    client: HttpClient,
    request: Request,
):

    token = authorization.credentials  # type: ignore
    await authenticate_token(token, client)

    response = await client.get(
        f"{settings.get_service_url(service_name=service)}/{path}",
        params=request.query_params,
        headers={"Authorization": token},
    )

    return response.json()


@app.delete("/protected/{service}/{path:path}")
async def route_delete_request(
    service: str,
    path: str,
    authorization: Auth,
    client: HttpClient,
    request: Request,
):
    token = authorization.credentials  # type: ignore
    await authenticate_token(token, client)

    response = await client.delete(
        f"{settings.get_service_url(service_name=service)}/{path}",
        params=request.query_params,
        headers={"Authorization": token},
    )

    return response.json()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
