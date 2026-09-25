"""Versioned acceptance of the Terms, Privacy Policy and Responsible Recovery policy."""
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth.supabase import CurrentUser, get_current_user
from config.settings import settings
from db.models import UserConsent
from db.session import get_db

CONSENT_REQUIRED = {
    "code": "consent_required",
    "message": "Please accept the Terms & Conditions and Privacy Policy to continue.",
}


def has_consent(db: Session, user_id: str) -> bool:
    return (
        db.scalar(
            select(UserConsent.id).where(
                UserConsent.user_id == user_id, UserConsent.terms_version == settings.terms_version
            )
        )
        is not None
    )


def record_consent(db: Session, user: CurrentUser, version: str, user_agent: str | None) -> None:
    if version != settings.terms_version:
        raise HTTPException(status.HTTP_409_CONFLICT, "The terms have changed. Reload the page and review them again.")
    if not has_consent(db, user.id):
        db.add(UserConsent(user_id=user.id, terms_version=version, user_agent=(user_agent or "")[:512]))
        db.commit()


def ensure_consent(db: Session, user: CurrentUser) -> None:
    if not has_consent(db, user.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, CONSENT_REQUIRED)


def require_consent(user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)) -> CurrentUser:
    ensure_consent(db, user)
    return user
