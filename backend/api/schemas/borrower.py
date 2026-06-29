"""Pydantic schemas for the borrower risk-prediction endpoint."""
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Gender(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"


class LoanType(str, Enum):
    personal = "Personal"
    auto = "Auto"
    business = "Business"
    home = "Home"


class BorrowerInput(BaseModel):
    """
    Everything the predictor form collects.

    `interest_rate` and `loan_tenure` are optional: if omitted, the backend
    fills them in from the loan type's default terms (mirrors the original
    app's "custom scheme" checkbox behavior — omit the fields to get
    defaults, supply them to override).
    """

    first_name: str = Field(..., min_length=1, max_length=80)
    last_name: str = Field(..., min_length=1, max_length=80)
    gender: Gender
    age: int = Field(..., ge=18, le=100)
    monthly_income: float = Field(..., gt=0, description="Monthly income in INR; must be greater than 0.")
    num_dependents: int = Field(..., ge=0)
    loan_type: LoanType
    loan_amount: float = Field(..., ge=10_000)
    collateral_value: float = Field(..., ge=0)
    outstanding_loan: float = Field(..., ge=0)
    missed_payments: int = Field(..., ge=0)
    interest_rate: float | None = Field(None, ge=0, le=100)
    loan_tenure: int | None = Field(None, ge=1, le=360)

    @field_validator("first_name", "last_name")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank")
        return v.strip()


class CalculatedFields(BaseModel):
    """Derived values shown to the user before/alongside the prediction."""

    monthly_emi: float
    days_past_due: int
    collection_attempts: int
    emi_to_income_ratio: float
    collateral_coverage: float
    default_severity: float
    interest_rate_used: float
    loan_tenure_used: int


class SegmentInfo(BaseModel):
    segment_id: int
    segment_name: str
    description: str


class ShapFeatureImpact(BaseModel):
    feature: str
    value: float
    shap_value: float
    direction: str  # "increased" | "decreased"
    description: str


class PredictionResult(BaseModel):
    borrower_id: str
    risk_score: float
    risk_category: str
    strategy: str
    calculated: CalculatedFields
    segment: SegmentInfo
    shap_top_features: list[ShapFeatureImpact]
    input: BorrowerInput
