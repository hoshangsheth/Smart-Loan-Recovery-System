"""Case persistence, access control, and audit logging."""
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.schemas.borrower import PredictionResult
from auth.supabase import CurrentUser
from db.models import AuditLog, Case, CaseBrief, Prediction


def _audit(db: Session, user: CurrentUser, action: str, entity_type: str, entity_id: str, **details) -> None:
    db.add(AuditLog(actor_id=user.id, action=action, entity_type=entity_type, entity_id=entity_id, details=details))


def _prediction_row(case_id: str, result: PredictionResult) -> Prediction:
    return Prediction(
        case_id=case_id,
        model_version=result.model_version,
        risk_score=result.risk_score,
        risk_category=result.risk_category,
        strategy=result.strategy,
        input=result.input.model_dump(mode="json"),
        calculated=result.calculated.model_dump(mode="json"),
        segment=result.segment.model_dump(mode="json"),
        shap_top_features=[f.model_dump(mode="json") for f in result.shap_top_features],
    )


def create_case(db: Session, user: CurrentUser, result: PredictionResult) -> Case:
    case = Case(
        borrower_ref=result.borrower_id,
        owner_id=user.id,
        first_name=result.input.first_name,
        last_name=result.input.last_name,
        loan_type=result.input.loan_type.value,
    )
    db.add(case)
    db.flush()
    prediction = _prediction_row(case.id, result)
    db.add(prediction)
    db.flush()
    _audit(db, user, "case.create", "case", case.id, prediction_id=prediction.id, risk_score=result.risk_score)
    db.commit()
    return case


def add_prediction(db: Session, user: CurrentUser, case: Case, result: PredictionResult) -> Prediction:
    prediction = _prediction_row(case.id, result)
    db.add(prediction)
    db.flush()
    _audit(db, user, "case.rescore", "case", case.id, prediction_id=prediction.id, risk_score=result.risk_score)
    db.commit()
    return prediction


def get_case(db: Session, user: CurrentUser, case_id: str) -> Case:
    case = db.get(Case, case_id)
    # 404 rather than 403 so officers can't probe for other officers' case IDs.
    if case is None or (not user.is_admin and case.owner_id != user.id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Case not found")
    return case


def list_cases(
    db: Session, user: CurrentUser, *, status_filter: str | None, limit: int, offset: int
) -> list[tuple[Case, Prediction | None]]:
    latest = (
        select(Prediction.case_id, func.max(Prediction.created_at).label("latest_at"))
        .group_by(Prediction.case_id)
        .subquery()
    )
    query = (
        select(Case, Prediction)
        .outerjoin(latest, latest.c.case_id == Case.id)
        .outerjoin(
            Prediction,
            (Prediction.case_id == Case.id) & (Prediction.created_at == latest.c.latest_at),
        )
        .order_by(Prediction.risk_score.desc().nulls_last(), Case.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if not user.is_admin:
        query = query.where(Case.owner_id == user.id)
    if status_filter:
        query = query.where(Case.status == status_filter)
    return [(row[0], row[1]) for row in db.execute(query).all()]


def update_status(db: Session, user: CurrentUser, case: Case, new_status: str) -> Case:
    old_status = case.status
    case.status = new_status
    _audit(db, user, "case.status", "case", case.id, old=old_status, new=new_status)
    db.commit()
    return case


def save_brief(db: Session, user: CurrentUser, brief: CaseBrief) -> CaseBrief:
    db.add(brief)
    db.flush()
    _audit(db, user, "brief.generate", "case", brief.case_id, brief_id=brief.id, llm_model=brief.llm_model)
    db.commit()
    return brief
