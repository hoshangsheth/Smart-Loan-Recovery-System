"""Verify Supabase-issued access tokens and expose the caller as a FastAPI dependency."""
from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config.settings import settings

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    id: str
    email: str | None
    role: str

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


@lru_cache
def _jwks_client() -> jwt.PyJWKClient:
    return jwt.PyJWKClient(f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json", cache_keys=True)


def decode_token(token: str) -> dict:
    if settings.supabase_jwt_secret:
        key, algorithms = settings.supabase_jwt_secret, ["HS256"]
    elif settings.supabase_url:
        key, algorithms = _jwks_client().get_signing_key_from_jwt(token).key, ["ES256", "RS256"]
    else:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Authentication is not configured")
    return jwt.decode(
        token,
        key,
        algorithms=algorithms,
        audience=settings.supabase_jwt_audience,
        options={"require": ["sub", "exp", "aud"]},
    )


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, detail, headers={"WWW-Authenticate": "Bearer"})


def get_optional_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser | None:
    if creds is None:
        return None
    try:
        claims = decode_token(creds.credentials)
    except (jwt.PyJWTError, jwt.PyJWKClientError) as exc:
        raise _unauthorized("Invalid or expired token") from exc
    return CurrentUser(
        id=claims["sub"],
        email=claims.get("email"),
        role=(claims.get("app_metadata") or {}).get("role", "officer"),
    )


def get_current_user(user: CurrentUser | None = Depends(get_optional_user)) -> CurrentUser:
    if user is None:
        raise _unauthorized("Authentication required")
    return user
