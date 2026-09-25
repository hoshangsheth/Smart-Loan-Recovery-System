"""
Prediction service: builds the model feature vector, runs the calibrated
model, and assigns the risk tier and recovery strategy.

Tier = the higher of (a) the tier implied by the calibrated probability and
(b) the regulatory floor for the account's RBI asset class. Critical needs
both a very high model probability and an NPA account.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd

from models.loader import MLArtifacts
from repository.constants import (
    ASSET_CLASSES,
    HIGH_RISK_THRESHOLD,
    MEDIUM_RISK_THRESHOLD,
    MODEL_FEATURE_ORDER,
    NPA_LABEL,
    POLICY_FLOOR_BY_ASSET_CLASS,
    RECOVERY_STRATEGIES,
    RISK_SCORE_BOUNDS,
    TIER_BANDS,
    TIER_ORDER,
    VERY_HIGH_RISK_THRESHOLD,
)
from services.feature_engineering import EngineeredFeatures


@dataclass(frozen=True)
class RiskAssessment:
    tier: str
    band: str
    label: str
    strategy: str
    asset_classification: str
    policy_override: str | None
    warning: str | None


def build_model_feature_vector(
    *,
    age: int,
    monthly_income: float,
    num_dependents: int,
    engineered: EngineeredFeatures,
    outstanding_loan: float,
) -> pd.DataFrame:
    """The 10 model features, named and ordered exactly as in training."""
    feature_map = {
        "Age": age,
        "Monthly_Income": monthly_income,
        "Num_Dependents": num_dependents,
        "Loan_Tenure": engineered.loan_tenure_used,
        "Interest_Rate": engineered.interest_rate_used,
        "Outstanding_Loan_Amount": outstanding_loan,
        "Collection_Attempts": engineered.collection_attempts,
        "EMI_to_Income_Ratio": engineered.emi_to_income_ratio or 0.0,
        "Collateral_Coverage": engineered.collateral_coverage or 0.0,
        "Default_Severity": engineered.default_severity,
    }
    return pd.DataFrame([[float(feature_map[name]) for name in MODEL_FEATURE_ORDER]], columns=MODEL_FEATURE_ORDER)


def predict_risk_score(artifacts: MLArtifacts, feature_vector: pd.DataFrame) -> float:
    """Calibrated probability that the loan will not be fully recovered."""
    raw = artifacts.xgb_model.predict_proba(feature_vector)[:, 1]
    calibrated = float(artifacts.calibrator.predict(raw)[0])
    return float(np.clip(calibrated, *RISK_SCORE_BOUNDS))


def classify_asset(days_past_due: int) -> str:
    for upper_bound, label in ASSET_CLASSES:
        if days_past_due <= upper_bound:
            return label
    return NPA_LABEL


def _model_tier(risk_score: float, asset_classification: str) -> str:
    if risk_score >= VERY_HIGH_RISK_THRESHOLD:
        return "critical" if asset_classification == NPA_LABEL else "high_no_dpd"
    if risk_score >= HIGH_RISK_THRESHOLD:
        return "high"
    if risk_score >= MEDIUM_RISK_THRESHOLD:
        return "medium"
    return "low"


def assess_risk(risk_score: float, days_past_due: int) -> RiskAssessment:
    asset_classification = classify_asset(days_past_due)
    tier = _model_tier(risk_score, asset_classification)
    policy_override = None

    floor = POLICY_FLOOR_BY_ASSET_CLASS.get(asset_classification)
    if floor and TIER_ORDER.index(tier) < TIER_ORDER.index(floor[0]):
        tier, policy_override = floor

    strategy = RECOVERY_STRATEGIES[tier]
    return RiskAssessment(
        tier=tier,
        band=TIER_BANDS[tier],
        label=strategy["label"],
        strategy=strategy["strategy"],
        asset_classification=asset_classification,
        policy_override=policy_override,
        warning=strategy.get("warning"),
    )
