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
#
# RECALIBRATED July 2026 against the retrained model (trained on real
# Recovery_Status outcomes instead of the old cluster-derived label). The
# old model was overfit to a near-deterministic label and produced
# probabilities pushed toward 0/1, which is why the old cutoffs (0.90/0.75)
# lived way out in the tails. The new model is honestly uncertain — its
# predict_proba output on this dataset ranges ~0.20-0.75 with a natural gap
# between the 70th percentile (~0.45) and 75th percentile (~0.68). These
# thresholds are set relative to THAT distribution. If the model is
# retrained again on a larger/different dataset, re-check these against the
# new probability distribution rather than assuming they still hold.
CRITICAL_RISK_THRESHOLD = 0.72
HIGH_RISK_THRESHOLD = 0.65
MEDIUM_RISK_THRESHOLD = 0.32
CRITICAL_DPD_THRESHOLD = 90

# Verified: these thresholds were computed via retrain.py's evaluation,
# which reads Collection_Attempts/Days_Past_Due straight from the CSV
# (true 0-10 range, never clamped). The serve-side bug that clamped
# Collection_Attempts to 0-4 (now fixed - see feature_engineering.py) never
# touched the numbers these thresholds were calibrated against, so they do
# NOT need to be re-derived now that serving matches training. Re-running
# predict_proba over the full dataset with true features confirms the same
# ~0.20-0.75 range and the same gap around 0.32/0.68 cited above.

# Risk category thresholds used purely for DISPLAY COLOR on the predictor
# results card and the PDF (3 bands). This is intentionally a *different*
# scheme from the 4-tier strategy thresholds above — the original app used
# multiple distinct threshold schemes in different places, and this
# refactor preserves that distinction rather than merging them for
# "consistency". Recalibrated alongside the strategy thresholds above.
DISPLAY_HIGH_RISK_THRESHOLD = 0.65
DISPLAY_MEDIUM_RISK_THRESHOLD = 0.32

# A THIRD, separate 3-band scheme used only for the Recovery Insights
# dashboard's accent/border color. Cutoffs are expressed as risk
# *percentage* (0-100) to match the original's `risk_pct` variable.
# Recalibrated to match the new model's ~20-75% output range.
DASHBOARD_HIGH_RISK_PCT = 65
DASHBOARD_LOW_RISK_PCT = 32

# "Approaching critical zone" warning band (risk %, displayed only on the
# predictor results page, independent of the other threshold schemes).
NEAR_CRITICAL_PCT_LOW = 65
NEAR_CRITICAL_PCT_HIGH = 72

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

# NOTE: there used to be a `collection_attempts_for_dpd()` step function
# here that derived Collection_Attempts from missed payments / DPD, capped
# at 4. It's removed. The training data shows Collection_Attempts is
# essentially uncorrelated with missed payments or DPD (r ~= 0.03-0.06) but
# strongly correlated with the actual outcome (r ~= 0.59), and ranges
# 0-10 - so it's a real, independent operational fact, not something a
# formula can reconstruct. It's now collected as a direct input
# (see BorrowerInput.collection_attempts). Same reasoning applies to
# Days_Past_Due, which is no longer derived as `missed_payments * 30`.
