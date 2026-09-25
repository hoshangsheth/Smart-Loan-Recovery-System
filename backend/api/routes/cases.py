"""Case queue, case detail, re-scoring, status changes, and AI briefs. All routes require auth."""
from fastapi import APIRouter, Depends, Query
from google import genai
from sqlalchemy.orm import Session

from api.schemas.borrower import BorrowerInput, PredictionResult
from api.schemas.case import CaseBriefOut, CaseDetail, CaseStatus, CaseStatusUpdate, CaseSummary
from auth.supabase import CurrentUser
from db.session import get_db
from models.loader import MLArtifacts, get_ml_artifacts
from services import brief_service, case_service
from services.consent_service import require_consent
from services.scoring_service import score_borrower

router = APIRouter(prefix="/cases", tags=["cases"])


def _detail(case) -> CaseDetail:
    return CaseDetail.model_validate(
        {
            **{k: getattr(case, k) for k in ("id", "borrower_ref", "first_name", "last_name", "loan_type", "status")},
            "created_at": case.created_at,
            "updated_at": case.updated_at,
            "predictions": case.predictions,
            "latest_brief": case.briefs[-1] if case.briefs else None,
        }
    )


@router.get("", response_model=list[CaseSummary])
def list_cases(
    status: CaseStatus | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: CurrentUser = Depends(require_consent),
    db: Session = Depends(get_db),
) -> list[CaseSummary]:
    rows = case_service.list_cases(
        db, user, status_filter=status.value if status else None, limit=limit, offset=offset
    )
    return [
        CaseSummary(
            id=case.id,
            borrower_ref=case.borrower_ref,
            first_name=case.first_name,
            last_name=case.last_name,
            loan_type=case.loan_type,
            status=case.status,
            latest_risk_score=pred.risk_score if pred else None,
            latest_risk_category=pred.risk_category if pred else None,
            latest_risk_band=pred.risk_band if pred else None,
            created_at=case.created_at,
            updated_at=case.updated_at,
        )
        for case, pred in rows
    ]


@router.get("/{case_id}", response_model=CaseDetail)
def get_case(case_id: str, user: CurrentUser = Depends(require_consent), db: Session = Depends(get_db)) -> CaseDetail:
    return _detail(case_service.get_case(db, user, case_id))


@router.post("/{case_id}/predictions", response_model=PredictionResult)
def rescore_case(
    case_id: str,
    payload: BorrowerInput,
    artifacts: MLArtifacts = Depends(get_ml_artifacts),
    user: CurrentUser = Depends(require_consent),
    db: Session = Depends(get_db),
) -> PredictionResult:
    case = case_service.get_case(db, user, case_id)
    result = score_borrower(payload, artifacts, borrower_id=case.borrower_ref)
    case_service.add_prediction(db, user, case, result)
    result.case_id = case.id
    return result


@router.patch("/{case_id}", response_model=CaseDetail)
def update_case_status(
    case_id: str,
    body: CaseStatusUpdate,
    user: CurrentUser = Depends(require_consent),
    db: Session = Depends(get_db),
) -> CaseDetail:
    case = case_service.get_case(db, user, case_id)
    return _detail(case_service.update_status(db, user, case, body.status.value))


@router.post("/{case_id}/brief", response_model=CaseBriefOut)
def generate_case_brief(
    case_id: str,
    user: CurrentUser = Depends(require_consent),
    db: Session = Depends(get_db),
    llm: genai.Client = Depends(brief_service.get_llm_client),
) -> CaseBriefOut:
    case = case_service.get_case(db, user, case_id)
    case_service.enforce_brief_quota(db, user)
    brief = brief_service.generate_brief(llm, case, case.predictions, user.id)
    return CaseBriefOut.model_validate(case_service.save_brief(db, user, brief))
