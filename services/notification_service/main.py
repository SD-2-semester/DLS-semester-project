import asyncio

import uvicorn
from api.routes.router import router as api_router
from fastapi import FastAPI
from rabbitmq.connection import setup_rabbitmq_consumers

app = FastAPI()

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Start the app, and run the rabbitmq as a background task."""

    # Run rabbitmq_consumer as a background task
    await asyncio.create_task(setup_rabbitmq_consumers())


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8081, reload=True)
