from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.endpoints import router as feedback_router
from app.database import (
    close_mongo_connection,
    connect_to_mongo,
    create_indexes,
    db_connection,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    await create_indexes()

    yield

    await close_mongo_connection()


app = FastAPI(title="Feedback AI API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feedback_router)


@app.get("/")
async def root():
    return {"message": "API is running"}


# Endpoint de santé utilisé par Docker et les outils de monitoring
# Vérifie que l'app tourne ET que la base de données répond
@app.get("/health")
async def health_check():
    try:
        # Envoie un ping à MongoDB pour vérifier la connexion
        await db_connection.client.admin.command("ping")
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {
        "status": "ok",
        "database": db_status,
    }
