from fastapi import FastAPI
import uvicorn
from api.routes.router import router as api_router
from rabbitmq.connection import rabbitmq_consumer
import asyncio

app = FastAPI()

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    await asyncio.create_task(
        rabbitmq_consumer()
    )  # Run rabbitmq_consumer as a background task


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8081, reload=True)
