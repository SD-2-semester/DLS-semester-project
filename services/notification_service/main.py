from fastapi import FastAPI, WebSocket
import uvicorn
from typing import Any


app = FastAPI()


@app.get("/")
async def test_yo() -> dict[Any, Any]:
    return {"data": "yo"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", port=8080, reload=True)
