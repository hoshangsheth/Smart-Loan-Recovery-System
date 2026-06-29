"""Schema for the analytics dashboard request."""
from pydantic import BaseModel, Field


class AnalyticsRequest(BaseModel):
    """
    Inputs needed to build the Recovery Insights dashboard charts.

    The frontend already has all of these values from the most recent
    `/predict` response (the calculated fields + original input + risk
    score) — this avoids re-deriving anything server-side and keeps the
    dashboard stateless on the backend.
    """

    emi_to_income_ratio: float = Field(..., ge=0)
    collateral_coverage: float = Field(..., ge=0)
    loan_tenure: int = Field(..., ge=1)
    missed_payments: int = Field(..., ge=0)
    loan_amount: float = Field(..., ge=0)
    collateral_value: float = Field(..., ge=0)
    risk_score: float = Field(..., ge=0, le=1)
