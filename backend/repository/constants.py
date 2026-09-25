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
# pipeline. NOTE: this was previously (incorrectly) documented as a
# 14-feature vector "distinct from" the model's 10-feature input. It is
# not — retrain.py trains both the KMeans segmentation and the XGBoost
# model on the identical 10-column FEATURES list. Kept as its own named
# constant (rather than reusing MODEL_FEATURE_ORDER directly) only so the
# two pipelines can be changed independently in the future without that
# implying they're currently different.
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

# --- Risk tiers -------------------------------------------------------------
# risk_score is a calibrated probability that the loan will NOT be fully
# recovered (see docs/MODEL_CARD.md), so these cutoffs are policy, not
# numbers tuned to one model's output range. They hold across retrains.
MEDIUM_RISK_THRESHOLD = 0.30
HIGH_RISK_THRESHOLD = 0.55
VERY_HIGH_RISK_THRESHOLD = 0.80

# Calibrated scores are clipped to this range: 500 training rows can't
# justify claiming certainty in either direction.
RISK_SCORE_BOUNDS = (0.02, 0.98)

# RBI early-stress classification by days past due (IRACP norms):
# SMA-0 1-30, SMA-1 31-60, SMA-2 61-90, NPA when overdue more than 90 days.
ASSET_CLASSES = [
    (0, "Standard"),
    (30, "SMA-0"),
    (60, "SMA-1"),
    (90, "SMA-2"),
]
NPA_LABEL = "NPA"

# Policy floors applied on top of the model: the regulatory stage of an
# account caps how low its tier can go, whatever the model says.
POLICY_FLOOR_BY_ASSET_CLASS = {
    NPA_LABEL: ("high", "NPA accounts (more than 90 days past due) are never below High Risk."),
    "SMA-2": ("medium", "SMA-2 accounts (61-90 days past due) are never below Medium Risk."),
}

TIER_ORDER = ["low", "medium", "high", "high_no_dpd", "critical"]

# UI color band per tier.
TIER_BANDS = {"low": "low", "medium": "medium", "high": "high", "high_no_dpd": "high", "critical": "critical"}

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
        "warning": (
            "The model rates this borrower very high risk. The case becomes Critical if it crosses 90 days past due."
        ),
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

# NOTE: there used to be a `collection_attempts_for_dpd()` step function
# here that derived Collection_Attempts from missed payments / DPD, capped
# at 4. It's removed. The training data shows Collection_Attempts is
# essentially uncorrelated with missed payments or DPD (r ~= 0.03-0.06) but
# strongly correlated with the actual outcome (r ~= 0.59), and ranges
# 0-10 - so it's a real, independent operational fact, not something a
# formula can reconstruct. It's now collected as a direct input
# (see BorrowerInput.collection_attempts). Same reasoning applies to
# Days_Past_Due, which is no longer derived as `missed_payments * 30`.
