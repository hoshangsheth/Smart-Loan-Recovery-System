"""
Feature engineering: every derived calculation used by the predictor.

`Days_Past_Due` and `Collection_Attempts` are DELIBERATELY NOT derived here.

They used to be computed from `missed_payments` via a step function capped
at 4, while the model was trained on the real CSV columns which range
0-10 and are almost uncorrelated with missed payments (r ~= 0.03-0.06 in
the training data) or with each other via any fixed formula (DPD is not a
clean multiple of missed payments either - r ~= 0.34). That mismatch meant
every borrower with a real Collection_Attempts > 4 - which in this dataset
is exactly the population that ends up At_Risk - had their strongest
signal (63% of total model feature importance) silently clipped at serve
time. There is no formula that recovers this; these are real operational
facts (how many times collections actually contacted the borrower, how
many actual days the account is past due) that only the recovery officer
filling in the form knows. They are collected as direct inputs in
`BorrowerInput` and passed straight through to `engineer_features()`.
"""
from repository.constants import FALLBACK_LOAN_TERMS, LOAN_TYPE_DEFAULTS


def get_default_loan_terms(loan_type: str) -> tuple[float, int]:
    """Default (interest_rate, tenure_months) for a loan type, with fallback."""
    terms = LOAN_TYPE_DEFAULTS.get(loan_type.lower(), FALLBACK_LOAN_TERMS)
    return terms.interest_rate, terms.tenure_months


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float | None:
    """
    Standard reducing-balance EMI formula.

    Returns None if any input is zero/missing, matching the original
    `calculate_emi()` guard clause exactly.
    """
    if not principal or not annual_rate or not tenure_months:
        return None
    r = annual_rate / (12 * 100)
    emi = (principal * r * (1 + r) ** tenure_months) / ((1 + r) ** tenure_months - 1)
    return round(emi, 2)


def calculate_emi_to_income(monthly_emi: float | None, monthly_income: float) -> float | None:
    if not monthly_income or not monthly_emi:
        return None
    return round(monthly_emi / monthly_income, 3)


def calculate_collateral_coverage(collateral_value: float, loan_amount: float) -> float | None:
    if not loan_amount or collateral_value is None:
        return None
    return round(collateral_value / loan_amount, 3)


def calculate_default_severity(missed_payments: int, days_past_due: int) -> float:
    return missed_payments * days_past_due


class EngineeredFeatures:
    """Convenience bundle holding every derived value for a single borrower."""

    def __init__(
        self,
        monthly_emi: float | None,
        days_past_due: int,
        collection_attempts: int,
        emi_to_income_ratio: float | None,
        collateral_coverage: float | None,
        default_severity: float,
        interest_rate_used: float,
        loan_tenure_used: int,
    ) -> None:
        self.monthly_emi = monthly_emi
        self.days_past_due = days_past_due
        self.collection_attempts = collection_attempts
        self.emi_to_income_ratio = emi_to_income_ratio
        self.collateral_coverage = collateral_coverage
        self.default_severity = default_severity
        self.interest_rate_used = interest_rate_used
        self.loan_tenure_used = loan_tenure_used


def engineer_features(
    *,
    loan_type: str,
    loan_amount: float,
    collateral_value: float,
    monthly_income: float,
    missed_payments: int,
    days_past_due: int,
    collection_attempts: int,
    interest_rate: float | None,
    loan_tenure: int | None,
) -> EngineeredFeatures:
    """
    Run the full derived-feature pipeline for one borrower.

    `days_past_due` and `collection_attempts` are real operational inputs
    from the recovery officer, not derived from `missed_payments` - see the
    module docstring for why that derivation was removed.

    If `interest_rate` / `loan_tenure` are not supplied, they default based
    on loan type (mirrors the "no custom scheme" path in the original app).
    """
    default_rate, default_tenure = get_default_loan_terms(loan_type)
    rate_used = interest_rate if interest_rate is not None else default_rate
    tenure_used = loan_tenure if loan_tenure is not None else default_tenure

    monthly_emi = calculate_emi(loan_amount, rate_used, tenure_used)
    emi_to_income_ratio = calculate_emi_to_income(monthly_emi, monthly_income)
    collateral_coverage = calculate_collateral_coverage(collateral_value, loan_amount)
    default_severity = calculate_default_severity(missed_payments, days_past_due)

    return EngineeredFeatures(
        monthly_emi=monthly_emi,
        days_past_due=days_past_due,
        collection_attempts=collection_attempts,
        emi_to_income_ratio=emi_to_income_ratio,
        collateral_coverage=collateral_coverage,
        default_severity=default_severity,
        interest_rate_used=rate_used,
        loan_tenure_used=tenure_used,
    )
