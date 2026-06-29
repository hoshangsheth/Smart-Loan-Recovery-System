"""Analytics route — returns structured chart-ready JSON, no rendering."""
from fastapi import APIRouter

from api.schemas.analytics import AnalyticsRequest
from services.analytics_service import build_analytics_bundle

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("")
def get_analytics(payload: AnalyticsRequest) -> dict:
    """Build every chart/insight the dashboard needs from a prior prediction's data."""
    return build_analytics_bundle(
        emi_to_income_ratio=payload.emi_to_income_ratio,
        collateral_coverage=payload.collateral_coverage,
        loan_tenure=payload.loan_tenure,
        missed_payments=payload.missed_payments,
        loan_amount=payload.loan_amount,
        collateral_value=payload.collateral_value,
        risk_score=payload.risk_score,
    )
