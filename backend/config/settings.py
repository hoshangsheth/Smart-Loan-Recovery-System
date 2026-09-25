"""
Centralized application configuration.

All environment-specific values (paths, URLs, secrets) are read here and
nowhere else. Every other module imports `settings` from this file instead
of calling `os.environ` or hardcoding values directly.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings, sourced from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    app_name: str = "Smart Loan Recovery System API"
    environment: str = "development"  # development | production
    api_v1_prefix: str = "/api/v1"

    # --- CORS ---
    # Comma-separated list of allowed frontend origins.
    cors_allowed_origins: str = "http://localhost:5173"

    # --- ML artifact paths ---
    # All paths are resolved relative to the backend root so the app can be
    # run from any working directory.
    ml_artifacts_dir: Path = Path(__file__).resolve().parent.parent / "ml_artifacts"
    xgb_model_path: Path = ml_artifacts_dir / "xgb_tuned.pkl"
    scaler_path: Path = ml_artifacts_dir / "scaler.pkl"
    kmeans_path: Path = ml_artifacts_dir / "kmeans.pkl"
    segment_names_path: Path = ml_artifacts_dir / "segment_names.pkl"
    gender_map_path: Path = ml_artifacts_dir / "gender_map.pkl"
    artifact_manifest_path: Path = ml_artifacts_dir / "manifest.json"

    # --- Database ---
    # Supabase: use the *session pooler* connection string (IPv4-compatible,
    # which Render free tier needs), with the psycopg driver prefix:
    # postgresql+psycopg://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
    database_url: str = "sqlite:///./recovia.db"

    # --- Auth (Supabase) ---
    # Leave supabase_jwt_secret empty for projects on asymmetric signing keys
    # (verified via JWKS); set it only for legacy HS256 projects.
    supabase_url: str = ""
    supabase_jwt_secret: str = ""
    supabase_jwt_audience: str = "authenticated"

    # --- LLM (Gemini) ---
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    gemini_thinking_level: str = "LOW"
    gemini_timeout_ms: int = 30_000

    # --- Contact ---
    whatsapp_number: str = "919004001598"  # international format, no '+' or spaces

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor — settings are read from env once per process."""
    return Settings()


settings = get_settings()
