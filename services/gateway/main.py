from fastapi import FastAPI, Request
from settings import settings
import httpx


app = FastAPI()


@app.route("/{service_name}/{path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_request(service_name: str, path: str, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=f"{settings.auth_service_url}/{service_name}/{path}",
            headers=request.headers,
            data=request.body,
        )

    return response.text, response.status_code, response.headers.items()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
    )
