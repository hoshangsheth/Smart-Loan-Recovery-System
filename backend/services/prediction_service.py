"""
Prediction service: builds the model feature vector, runs inference, and
assigns the risk category + recovery strategy.

This mirrors `assign_recovery_strategy()` and the model-call block in the
original `slrs.py` exactly — including keeping the 4-tier strategy
thresholds and the 3-band display-color thresholds as two distinct schemes
(see repository/constants.py for why).
"""
import numpy as np

from models.loader import MLArtifacts
from repository.constants import (
    CRITICAL_DPD_THRESHOLD,
    CRITICAL_RISK_THRESHOLD,
    DASHBOARD_HIGH_RISK_PCT,
    DASHBOARD_LOW_RISK_PCT,
    DISPLAY_HIGH_RISK_THRESHOLD,
    DISPLAY_MEDIUM_RISK_THRESHOLD,
    HIGH_RISK_THRESHOLD,
    MEDIUM_RISK_THRESHOLD,
    MODEL_FEATURE_ORDER,
    NEAR_CRITICAL_PCT_HIGH,
    NEAR_CRITICAL_PCT_LOW,
    RECOVERY_STRATEGIES,
)
from services.feature_engineering import EngineeredFeatures


def build_model_feature_vector(
    *,
    age: int,
    monthly_income: float,
    num_dependents: int,
    engineered: EngineeredFeatures,
    outstanding_loan: float,
) -> np.ndarray:
    """
    Assemble the exact 10-feature vector the XGBoost model expects, in the
    exact order it was trained on (see MODEL_FEATURE_ORDER).
    """
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
    ordered = [feature_map[name] for name in MODEL_FEATURE_ORDER]
    return np.array(ordered, dtype=float).reshape(1, -1)


def predict_risk_score(artifacts: MLArtifacts, feature_vector: np.ndarray) -> float:
    """Run the XGBoost classifier and return P(default) as a float in [0, 1]."""
    proba = artifacts.xgb_model.predict_proba(feature_vector)
    return float(proba[0][1])


def assign_recovery_strategy(risk_score: float, days_past_due: int) -> dict:
    """
    4-tier strategy assignment based on risk score AND days past due.

    Ported verbatim from the original `assign_recovery_strategy()`.
    """
    if risk_score > CRITICAL_RISK_THRESHOLD and days_past_due >= CRITICAL_DPD_THRESHOLD:
        return RECOVERY_STRATEGIES["critical"]
    if risk_score > CRITICAL_RISK_THRESHOLD:
        return RECOVERY_STRATEGIES["high_no_dpd"]
    if risk_score > HIGH_RISK_THRESHOLD:
        return RECOVERY_STRATEGIES["high"]
    if risk_score > MEDIUM_RISK_THRESHOLD:
        return RECOVERY_STRATEGIES["medium"]
    return RECOVERY_STRATEGIES["low"]


def get_display_risk_band(risk_score: float) -> str:
    """
    3-band scheme used purely for UI color coding on the predictor results
    card and PDF (red/amber/green).

    Deliberately separate from the 4-tier strategy thresholds above.
    """
    if risk_score > DISPLAY_HIGH_RISK_THRESHOLD:
        return "high"
    if risk_score > DISPLAY_MEDIUM_RISK_THRESHOLD:
        return "medium"
    return "low"


def get_dashboard_risk_band(risk_score: float) -> str:
    """
    A THIRD, separate 3-band scheme used only for the Recovery Insights
    dashboard's accent/border color. Cutoffs differ from
    `get_display_risk_band` — this is intentional, matching the original
    app's two independently-defined color schemes.
    """
    risk_pct = risk_score * 100
    if risk_pct < DASHBOARD_LOW_RISK_PCT:
        return "low"
    if risk_pct <= DASHBOARD_HIGH_RISK_PCT:
        return "medium"
    return "high"


def is_approaching_critical_zone(risk_score: float) -> bool:
    """
    True when risk is in the 80-85% band, triggering the "could enter the
    Critical Zone" warning shown on the predictor results page.
    """
    risk_pct = risk_score * 100
    return NEAR_CRITICAL_PCT_LOW <= risk_pct < NEAR_CRITICAL_PCT_HIGH
