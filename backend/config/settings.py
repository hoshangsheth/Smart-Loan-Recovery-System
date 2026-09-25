"""
Centralized application configuration.

All environment-specific values (paths, URLs, secrets) are read here and
nowhere else. Every other module imports `settings` from this file instead
of calling `os.environ` or hardcoding values directly.
"""
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote, unquote

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    """
    Accept the connection string exactly as Supabase's dashboard shows it:
    add the psycopg driver, URL-encode the password, and drop the brackets
    left over from its [YOUR-PASSWORD] placeholder.
    """
    url = url.strip()
    scheme, sep, rest = url.partition("://")
    if not sep or scheme not in ("postgres", "postgresql", "postgresql+psycopg"):
        return url
    creds, at, host = rest.rpartition("@")
    if at and ":" in creds:
        user, _, password = creds.partition(":")
        if password.startswith("[") and password.endswith("]"):
            password = password[1:-1]
        rest = f"{user}:{quote(unquote(password), safe='')}@{host}"
    return f"postgresql+psycopg://{rest}"


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
    calibrator_path: Path = ml_artifacts_dir / "calibrator.pkl"
    segment_profiles_path: Path = ml_artifacts_dir / "segment_profiles.pkl"
    artifact_manifest_path: Path = ml_artifacts_dir / "manifest.json"

    # --- Database ---
    # Supabase: paste the *session pooler* string as-is (IPv4-compatible,
    # which Render free tier needs); normalize_database_url() fixes it up.
    database_url: str = "sqlite:///./recovia.db"

    @field_validator("database_url")
    @classmethod
    def _normalize_database_url(cls, v: str) -> str:
        return normalize_database_url(v)

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
    # Anyone can sign up, so cap paid LLM calls per non-admin user (rolling 24h).
    brief_daily_limit_per_user: int = 20

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
