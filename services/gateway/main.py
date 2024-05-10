from fastapi import FastAPI, Request
from settings import settings
from httpx import AsyncClient
from typing import Any
from fastapi.responses import UJSONResponse


app = FastAPI(
    title="gateway",
    docs_url="/gateway/api/docs",
    redoc_url="/gateway/api/redoc",
    openapi_url="/gateway/api/openapi.json",
    default_response_class=UJSONResponse,
)


@app.route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_request(
    service: str,
    path: str,
    request: Request,
    protected: bool = False,
) -> Any:
    """Route request to the appropriate service."""

    async with AsyncClient() as client:
        try:
            response = await client.request(
                request.method,
                f"http://{service}/{path}",
                headers=request.headers if protected else None,
                data=request.body,  # type: ignore
            )
        except Exception as e:
            return {"error": str(e)}

    return response.json()["data"]


@app.get("/")
def test():
    return {"message": "Hello, world!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
