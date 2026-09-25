"""
Borrower segmentation service.

This is intentionally isolated from `prediction_service.py`: the
segmentation pipeline (StandardScaler -> KMeans) was trained independently
of the XGBoost risk model, on a different 14-feature schema, and produces a
business-facing label ("High Income, Low Default Risk") rather than a risk
score. Keeping it in its own service means either pipeline can change
without touching the other.
"""
import pandas as pd

from models.loader import MLArtifacts
from repository.constants import SEGMENTATION_FEATURE_ORDER
from services.feature_engineering import EngineeredFeatures


def build_segmentation_feature_vector(
    *,
    age: int,
    monthly_income: float,
    num_dependents: int,
    outstanding_loan: float,
    engineered: EngineeredFeatures,
) -> pd.DataFrame:
    """
    Assemble the 14-feature vector the scaler/KMeans pipeline expects.

    Distinct feature set and order from the model's 10-feature vector —
    see SEGMENTATION_FEATURE_ORDER in repository/constants.py.
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
    return pd.DataFrame(
        [[float(feature_map[name]) for name in SEGMENTATION_FEATURE_ORDER]], columns=SEGMENTATION_FEATURE_ORDER
    )


def assign_segment(artifacts: MLArtifacts, raw_feature_vector: pd.DataFrame) -> dict:
    """
    Scale the raw 10-feature vector and predict its KMeans cluster.

    Returns a dict with segment_id, segment_name, and a plain-language
    business description suitable for display in the dashboard and PDF.
    """
    scaled = artifacts.scaler.transform(raw_feature_vector)
    cluster_id = int(artifacts.kmeans.predict(scaled)[0])
    profile = artifacts.segment_profiles[cluster_id]
    return {
        "segment_id": cluster_id,
        "segment_name": profile["name"],
        "description": profile["description"],
    }
