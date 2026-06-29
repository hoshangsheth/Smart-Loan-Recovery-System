"""
Application entrypoint.

Wires up CORS, route registration, and the startup hook that loads every
ML artifact exactly once before the app starts serving requests.
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import analytics, contact, predict, report
from config.settings import settings
from models.loader import get_ml_artifacts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def load_models_on_startup() -> None:
    """Load all ML artifacts once, at process startup, never per-request."""
    get_ml_artifacts()
    logger.info("Startup complete — all ML artifacts loaded.")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


app.include_router(predict.router, prefix=settings.api_v1_prefix)
app.include_router(analytics.router, prefix=settings.api_v1_prefix)
app.include_router(report.router, prefix=settings.api_v1_prefix)
app.include_router(contact.router, prefix=settings.api_v1_prefix)
