"""
Prediction route.

Anonymous callers get a score and nothing is stored. Signed-in callers also
get a persisted case they can come back to.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.schemas.borrower import BorrowerInput, PredictionResult
from auth.supabase import CurrentUser, get_optional_user
from db.session import get_db
from models.loader import MLArtifacts, get_ml_artifacts
from services import case_service
from services.scoring_service import score_borrower

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("", response_model=PredictionResult)
def predict_risk(
    payload: BorrowerInput,
    artifacts: MLArtifacts = Depends(get_ml_artifacts),
    user: CurrentUser | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> PredictionResult:
    result = score_borrower(payload, artifacts)
    if user is not None:
        case = case_service.create_case(db, user, result)
        result.case_id = case.id
    return result
