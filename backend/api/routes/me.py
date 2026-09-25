"""The signed-in user's consent status and AI brief allowance."""
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.supabase import CurrentUser, get_current_user
from config.settings import settings
from db.session import get_db
from services import case_service, consent_service

router = APIRouter(prefix="/me", tags=["me"])


class BriefUsage(BaseModel):
    used: int
    limit: int | None
    resets_at: datetime | None


class Me(BaseModel):
    id: str
    email: str | None
    is_admin: bool
    terms_version: str
    consent_required: bool
    ai_briefs_enabled: bool
    briefs: BriefUsage


class ConsentIn(BaseModel):
    terms_version: str


def _me(db: Session, user: CurrentUser) -> Me:
    return Me(
        id=user.id,
        email=user.email,
        is_admin=user.is_admin,
        terms_version=settings.terms_version,
        consent_required=not consent_service.has_consent(db, user.id),
        ai_briefs_enabled=bool(settings.gemini_api_key),
        briefs=case_service.brief_usage(db, user),
    )


@router.get("", response_model=Me)
def get_me(user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)) -> Me:
    return _me(db, user)


@router.post("/consent", response_model=Me)
def accept_terms(
    body: ConsentIn,
    request: Request,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Me:
    consent_service.record_consent(db, user, body.terms_version, request.headers.get("user-agent"))
    return _me(db, user)
