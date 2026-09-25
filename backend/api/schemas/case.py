from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from api.schemas.borrower import CalculatedFields, SegmentInfo, ShapFeatureImpact


class CaseStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    written_off = "written_off"


class RecommendedAction(BaseModel):
    action: str = Field(description="One concrete next step for the recovery officer.")
    rationale: str = Field(description="Why, tied to a specific metric or risk driver in the case data.")
    priority: Literal["immediate", "this_week", "monitor"]
    channel: Literal["call", "sms", "email", "whatsapp", "field_visit", "legal_notice", "internal"]


class CaseBriefContent(BaseModel):
    """Structured output schema Gemini must fill."""

    summary: str = Field(description="3-4 sentence plain-language situation summary for a recovery officer.")
    key_risk_drivers: list[str] = Field(description="2-4 bullets explaining what drives the risk, citing numbers.")
    recommended_actions: list[RecommendedAction] = Field(description="2-4 actions, most urgent first.")
    outreach_draft: str = Field(
        description="A short, respectful first-contact message to the borrower. "
        "Use the placeholder {borrower_name}; never invent names, amounts or deadlines not in the data."
    )
    caveats: list[str] = Field(description="Data gaps or reasons to double-check before acting. May be empty.")


class CaseBriefOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    prediction_id: str
    llm_model: str
    prompt_version: str
    content: CaseBriefContent
    latency_ms: int
    input_tokens: int | None
    output_tokens: int | None
    created_at: datetime


class PredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    model_version: str
    risk_score: float
    risk_category: str
    strategy: str
    calculated: CalculatedFields
    segment: SegmentInfo
    shap_top_features: list[ShapFeatureImpact]
    created_at: datetime


class CaseSummary(BaseModel):
    id: str
    borrower_ref: str
    first_name: str
    last_name: str
    loan_type: str
    status: CaseStatus
    latest_risk_score: float | None
    latest_risk_category: str | None
    created_at: datetime
    updated_at: datetime


class CaseDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    borrower_ref: str
    first_name: str
    last_name: str
    loan_type: str
    status: CaseStatus
    created_at: datetime
    updated_at: datetime
    predictions: list[PredictionOut]
    latest_brief: CaseBriefOut | None


class CaseStatusUpdate(BaseModel):
    status: CaseStatus
