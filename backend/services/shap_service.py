"""
SHAP explainability service.

The original app rendered a matplotlib "waterfall_legacy" plot. This
service computes the identical SHAP values via the same TreeExplainer, but
serializes them as plain JSON instead of an image — the frontend renders
its own chart from this data. The plain-language feature descriptions and
directional wording are ported verbatim from the original.
"""
import numpy as np

from models.loader import MLArtifacts
from repository.constants import MODEL_FEATURE_ORDER

# Human-readable labels for the SHAP chart axis — matches the original
# app's `feature_names` list used purely for the SHAP plot (distinct from
# the internal MODEL_FEATURE_ORDER keys).
SHAP_DISPLAY_NAMES = {
    "Age": "Age",
    "Monthly_Income": "Monthly Income",
    "Num_Dependents": "Dependents",
    "Loan_Tenure": "Loan Tenure",
    "Interest_Rate": "Interest Rate",
    "Outstanding_Loan_Amount": "Outstanding Loan",
    "Collection_Attempts": "Collection Attempts",
    "EMI_to_Income_Ratio": "EMI to Income",
    "Collateral_Coverage": "Collateral Coverage",
    "Default_Severity": "Default Severity",
}

_PLAIN_LANGUAGE_DESCRIPTIONS = {
    "EMI to Income": "A high EMI to Income ratio means a large part of income goes to loan payments, increasing risk.",
    "Collateral Coverage": "Lower collateral coverage means less security for the lender, raising risk.",
    "Default Severity": "More missed payments or higher default severity increases the risk of default.",
    "Outstanding Loan": "A higher outstanding loan amount increases the lender's exposure.",
    "Monthly Income": "Higher monthly income generally reduces risk, while lower income increases it.",
    "Age": "Borrower's age can affect risk, with very young or old ages sometimes increasing risk.",
    "Loan Tenure": "Longer loan tenure can increase risk due to longer exposure.",
    "Interest Rate": "Higher interest rates can increase repayment burden and risk.",
    "Dependents": "More dependents may mean higher financial obligations, increasing risk.",
    "Collection Attempts": "More collection attempts indicate repayment issues, raising risk.",
}


def _describe_feature(display_name: str) -> str:
    return _PLAIN_LANGUAGE_DESCRIPTIONS.get(
        display_name, f"Feature '{display_name}' has a notable impact on risk."
    )


def compute_shap_top_features(
    artifacts: MLArtifacts, feature_vector: np.ndarray, top_n: int = 3
) -> list[dict]:
    """
    Compute SHAP values for one borrower and return the top-N most
    impactful features as plain dicts (feature, value, shap_value,
    direction, description), ready to serialize as JSON.
    """
    import shap  # imported lazily — heavy dependency, only needed here

    explainer = shap.TreeExplainer(artifacts.xgb_model)
    shap_values = explainer.shap_values(feature_vector)

    row_values = shap_values[0]
    abs_impact = np.abs(row_values)
    top_idx = np.argsort(abs_impact)[::-1][:top_n]

    results = []
    for idx in top_idx:
        internal_name = MODEL_FEATURE_ORDER[idx]
        display_name = SHAP_DISPLAY_NAMES[internal_name]
        value = float(feature_vector[0][idx])
        impact = float(row_values[idx])
        direction = "increased" if impact > 0 else "decreased"
        results.append(
            {
                "feature": display_name,
                "value": value,
                "shap_value": impact,
                "direction": direction,
                "description": _describe_feature(display_name),
            }
        )
    return results


def build_non_shap_insights(
    *,
    emi_to_income_ratio: float | None,
    missed_payments: int,
    collateral_value: float,
    collateral_coverage: float | None,
) -> list[str]:
    """
    The rule-based (non-SHAP) insight bullets: EMI burden, missed payments,
    and collateral coverage. Ported verbatim from the original app.
    """
    insights: list[str] = []

    if emi_to_income_ratio is not None:
        if emi_to_income_ratio > 0.5:
            insights.append("EMI burden exceeds 50% of income")
        elif emi_to_income_ratio > 0.35:
            insights.append("EMI burden is moderate (35-50% of income)")
        else:
            insights.append("EMI burden is low relative to income")

    if missed_payments is not None:
        if missed_payments >= 4:
            insights.append(f"Missed {missed_payments} EMIs \u2192 indicates growing payment fatigue")
        elif missed_payments > 0:
            insights.append(f"Missed {missed_payments} EMI{'s' if missed_payments > 1 else ''} recently")
        else:
            insights.append("No missed EMIs - good repayment track record")

    if collateral_value == 0:
        insights.append("No collateral \u2192 unsecured risk exposure")
    elif collateral_coverage is not None:
        if collateral_coverage < 1:
            insights.append("Collateral value is less than loan amount - higher risk in default")
        elif collateral_coverage == 1:
            insights.append("Collateral matches loan amount - basic security")
        else:
            insights.append("Collateral exceeds loan amount - strong security")

    return insights[:3]
