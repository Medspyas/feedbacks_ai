from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import connect_to_mongo, close_mongo_connection

from app.api.v1.endpoints import router as feedback_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()

    yield

    await close_mongo_connection()

app = FastAPI(title="Feedback AI API", lifespan=lifespan)

app.include_router(feedback_router)

@app.get("/")
async def root():
    return{"message": "API is running"}