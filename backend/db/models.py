import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

JSONType = JSON().with_variant(JSONB(), "postgresql")


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    borrower_ref: Mapped[str] = mapped_column(String(64), index=True)
    owner_id: Mapped[str] = mapped_column(String(64), index=True)
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    loan_type: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="open", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    predictions: Mapped[list["Prediction"]] = relationship(
        back_populates="case", order_by="Prediction.created_at", cascade="all, delete-orphan"
    )
    briefs: Mapped[list["CaseBrief"]] = relationship(
        back_populates="case", order_by="CaseBrief.created_at", cascade="all, delete-orphan"
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    model_version: Mapped[str] = mapped_column(String(32))
    risk_score: Mapped[float] = mapped_column(Float)
    risk_category: Mapped[str] = mapped_column(String(64))
    risk_tier: Mapped[str | None] = mapped_column(String(32), nullable=True)
    risk_band: Mapped[str | None] = mapped_column(String(16), nullable=True)
    asset_classification: Mapped[str | None] = mapped_column(String(16), nullable=True)
    policy_override: Mapped[str | None] = mapped_column(Text, nullable=True)
    strategy: Mapped[str] = mapped_column(Text)
    input: Mapped[dict] = mapped_column(JSONType)
    calculated: Mapped[dict] = mapped_column(JSONType)
    segment: Mapped[dict] = mapped_column(JSONType)
    shap_top_features: Mapped[list] = mapped_column(JSONType)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)

    case: Mapped[Case] = relationship(back_populates="predictions")


class CaseBrief(Base):
    __tablename__ = "case_briefs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    prediction_id: Mapped[str] = mapped_column(ForeignKey("predictions.id", ondelete="CASCADE"))
    created_by: Mapped[str] = mapped_column(String(64))
    llm_model: Mapped[str] = mapped_column(String(64))
    prompt_version: Mapped[str] = mapped_column(String(32))
    content: Mapped[dict] = mapped_column(JSONType)
    latency_ms: Mapped[int] = mapped_column(Integer)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    case: Mapped[Case] = relationship(back_populates="briefs")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    actor_id: Mapped[str] = mapped_column(String(64), index=True)
    action: Mapped[str] = mapped_column(String(64))
    entity_type: Mapped[str] = mapped_column(String(32))
    entity_id: Mapped[str] = mapped_column(String(36), index=True)
    details: Mapped[dict] = mapped_column(JSONType, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class UserConsent(Base):
    __tablename__ = "user_consents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    terms_version: Mapped[str] = mapped_column(String(32))
    accepted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
