"""Schema for the PDF report generation request."""
from pydantic import BaseModel


class ReportRequest(BaseModel):
    """
    Everything needed to regenerate the borrower's PDF report.

    The backend holds no session state, so the frontend sends back the
    full prediction result (received from `/predict`) along with the two
    original-form flags (loan_type label, whether a custom scheme was
    applied) that only the PDF needs verbatim.
    """

    borrower_id: str
    first_name: str
    last_name: str
    gender: str
    age: int
    loan_type: str
    custom_scheme: bool
    monthly_income: float
    loan_amount: float
    outstanding_loan: float
    loan_tenure: int
    interest_rate: float
    collateral_value: float
    missed_payments: int
    days_past_due: int
    collection_attempts: int
    monthly_emi: float
    emi_to_income: float
    collateral_coverage: float
    default_severity: float
    risk_score: float
    risk_category: str
    strategy: str
    segment_name: str
    segment_description: str
