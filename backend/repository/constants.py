"""
Static business-rule data: loan-type defaults, risk thresholds, and
recovery-strategy text.

These values are ported verbatim from the original `slrs.py` Streamlit app.
Nothing here is invented — every threshold and string matches the legacy
behavior exactly, so predictions and strategy text remain identical after
the refactor.
"""
from typing import NamedTuple


class LoanTerms(NamedTuple):
    interest_rate: float
    tenure_months: int


# Default interest rate (%) and tenure (months) per loan type.
# Mirrors `get_default_loan_terms()` in the original slrs.py.
LOAN_TYPE_DEFAULTS: dict[str, LoanTerms] = {
    "personal": LoanTerms(14.0, 48),
    "auto": LoanTerms(10.5, 60),
    "business": LoanTerms(16.0, 36),
    "home": LoanTerms(9.0, 180),
}
FALLBACK_LOAN_TERMS = LoanTerms(15.0, 36)

LOAN_TYPES = ["Personal", "Auto", "Business", "Home"]

# Model feature order — the XGBoost model is brittle to ordering; this list
# is the single source of truth for how the 10-feature vector is assembled.
MODEL_FEATURE_ORDER = [
    "Age",
    "Monthly_Income",
    "Num_Dependents",
    "Loan_Tenure",
    "Interest_Rate",
    "Outstanding_Loan_Amount",
    "Collection_Attempts",
    "EMI_to_Income_Ratio",
    "Collateral_Coverage",
    "Default_Severity",
]

# Feature order expected by the (separate) scaler/KMeans segmentation
# pipeline. This is a 14-feature vector, distinct from the 10-feature model
# input above — the two pipelines were trained independently.
SEGMENTATION_FEATURE_ORDER = [
    "Age",
    "Monthly_Income",
    "Num_Dependents",
    "Loan_Tenure",
    "Interest_Rate",
    "Outstanding_Loan_Amount",
    "Collection_Attempts",
    "EMI_to_Income_Ratio",
    "Collateral_Coverage",
    "Default_Severity",
]

# Plain-business-language descriptions for each KMeans segment.
# The cluster ID -> name mapping itself comes from segment_names.pkl at
# runtime; this dict supplies the longer explanation shown in the UI/PDF,
# keyed by the segment *name* (so it stays correct even if cluster IDs are
# ever re-ordered by a future re-training).
SEGMENT_DESCRIPTIONS: dict[str, str] = {
    "Moderate Income, High Loan Burden": (
        "This borrower carries a loan that is large relative to their income. "
        "Repayment capacity is moderate, so EMI restructuring or income "
        "verification can meaningfully reduce risk."
    ),
    "High Income, Low Default Risk": (
        "This borrower's income comfortably covers their obligations and "
        "their historical default risk is low. Standard monitoring is "
        "typically sufficient."
    ),
    "Moderate Income, Medium Risk": (
        "This borrower sits in the middle of the risk spectrum — income is "
        "adequate but not high, with some signs of repayment strain. Regular "
        "check-ins help catch early warning signs."
    ),
    "High Loan, Higher Default Risk": (
        "This borrower has a large loan exposure combined with elevated "
        "historical default risk. Closer collections attention and stronger "
        "collateral coverage are recommended."
    ),
}

# Risk category thresholds used for the recovery STRATEGY (4 tiers, depends
# on both risk score and Days Past Due). Mirrors `assign_recovery_strategy`.
CRITICAL_RISK_THRESHOLD = 0.90
HIGH_RISK_THRESHOLD = 0.75
MEDIUM_RISK_THRESHOLD = 0.25
CRITICAL_DPD_THRESHOLD = 90

# Risk category thresholds used purely for DISPLAY COLOR on the predictor
# results card and the PDF (3 bands). This is intentionally a *different*
# scheme from the 4-tier strategy thresholds above — the original app used
# multiple distinct threshold schemes in different places, and this
# refactor preserves that distinction rather than merging them for
# "consistency".
DISPLAY_HIGH_RISK_THRESHOLD = 0.75
DISPLAY_MEDIUM_RISK_THRESHOLD = 0.25

# A THIRD, separate 3-band scheme used only for the Recovery Insights
# dashboard's accent/border color. Cutoffs are expressed as risk
# *percentage* (0-100) to match the original's `risk_pct` variable.
DASHBOARD_HIGH_RISK_PCT = 85
DASHBOARD_LOW_RISK_PCT = 35

# "Approaching critical zone" warning band (risk %, displayed only on the
# predictor results page, independent of the other threshold schemes).
NEAR_CRITICAL_PCT_LOW = 80
NEAR_CRITICAL_PCT_HIGH = 85

RECOVERY_STRATEGIES = {
    "critical": {
        "label": "Critical Risk",
        "strategy": (
            "Initiate legal proceedings, send final demand notices with collateral seizure intent, "
            "escalate case to external recovery agencies, and flag borrower as a chronic defaulter."
        ),
    },
    "high_no_dpd": {
        "label": "High Risk",
        "strategy": (
            "Send pre-litigation warning, offer limited time restructuring, and escalate to senior recovery team."
        ),
    },
    "high": {
        "label": "High Risk",
        "strategy": (
            "Offer one-time settlement options or revised repayment terms, "
            "escalate to senior collections team, and issue a pre-litigation warning."
        ),
    },
    "medium": {
        "label": "Medium Risk",
        "strategy": (
            "Trigger multiple soft recovery attempts including calls, emails, and WhatsApp nudges. "
            "Offer flexible EMI restructuring plans and conduct borrower behavior analysis."
        ),
    },
    "low": {
        "label": "Low Risk",
        "strategy": (
            "Send timely automated reminders via SMS/email, monitor payment behavior closely, "
            "and provide financial advisory nudges to maintain repayment consistency."
        ),
    },
}

# Collection attempts step-function (based on Days Past Due).
def collection_attempts_for_dpd(missed_payments: int, days_past_due: int) -> int:
    """Mirrors the inline logic in the original predictor page exactly."""
    if missed_payments == 0:
        return 0
    if days_past_due <= 30:
        return 1
    if 31 <= days_past_due <= 60:
        return 2
    if 61 <= days_past_due <= 90:
        return 3
    return 4
