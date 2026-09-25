"""
Application entrypoint.

Wires up CORS, route registration, and the startup hook that loads every
ML artifact exactly once before the app starts serving requests.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from api.routes import analytics, cases, contact, me, predict, report
from config.settings import settings
from db.session import get_engine
from models.loader import get_ml_artifacts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.environment == "production" and settings.database_url.startswith("sqlite"):
        raise RuntimeError("DATABASE_URL must point at Postgres in production; container SQLite is wiped on redeploy")
    get_ml_artifacts()
    logger.info("Startup complete — all ML artifacts loaded.")
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/health/ready")
def readiness_check() -> dict:
    """Checks the DB too; the daily keepalive job hits this so Supabase free tier never pauses."""
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        logger.exception("Readiness check failed")
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ok", "model_version": get_ml_artifacts().model_version}


app.include_router(predict.router, prefix=settings.api_v1_prefix)
app.include_router(cases.router, prefix=settings.api_v1_prefix)
app.include_router(me.router, prefix=settings.api_v1_prefix)
app.include_router(analytics.router, prefix=settings.api_v1_prefix)
app.include_router(report.router, prefix=settings.api_v1_prefix)
app.include_router(contact.router, prefix=settings.api_v1_prefix)
