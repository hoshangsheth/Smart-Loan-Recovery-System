"""
Analytics service.

The original app computed Plotly figures server-side (inside Streamlit).
Here the backend only computes the underlying numbers; the frontend owns
all rendering (Recharts/D3/etc.), matching the brief's separation between
analytics calculations and chart UI.
"""
from repository.constants import DASHBOARD_HIGH_RISK_PCT, DASHBOARD_LOW_RISK_PCT


def build_feature_percentage_chart(emi_to_income_ratio: float, collateral_coverage: float) -> dict:
    """Bar chart data: EMI-to-Income % vs Collateral Coverage %."""
    emi_pct = round(emi_to_income_ratio * 100, 2)
    coverage_pct = round(collateral_coverage * 100, 2)
    return {
        "type": "bar",
        "data": [
            {"label": "EMI to Income Ratio (%)", "value": emi_pct},
            {"label": "Collateral Coverage (%)", "value": coverage_pct},
        ],
        "caption": (
            f"EMI to Income Ratio: {emi_pct:.2f}%. Collateral Coverage: {coverage_pct:.2f}%. "
            "Higher EMI/Income or lower Collateral Coverage may indicate higher risk."
        ),
    }


def build_payment_history_chart(loan_tenure: int, missed_payments: int) -> dict | None:
    """Donut chart data: paid vs missed EMIs. None if tenure is 0 (no chart)."""
    if loan_tenure <= 0:
        return None
    paid = max(loan_tenure - missed_payments, 0)
    return {
        "type": "donut",
        "data": [
            {"label": "Paid", "value": paid, "color": "#388e3c"},
            {"label": "Missed", "value": missed_payments, "color": "#d32f2f"},
        ],
        "caption": f"Missed Payments: {missed_payments} out of {loan_tenure} total EMIs.",
    }


def build_loan_vs_collateral_chart(loan_amount: float, collateral_value: float) -> dict:
    """Pie chart data: loan amount vs collateral value as % of total exposure."""
    total = loan_amount + collateral_value
    if total > 0:
        loan_pct = round(loan_amount / total * 100, 2)
        collateral_pct = round(collateral_value / total * 100, 2)
        caption = (
            f"Loan Amount: {loan_pct:.2f}%, Collateral Value: {collateral_pct:.2f}% of total exposure. "
            "Higher collateral coverage reduces risk."
        )
    else:
        loan_pct = 0.0
        collateral_pct = 0.0
        caption = "No loan or collateral value entered."

    return {
        "type": "pie",
        "data": [
            {"label": "Loan Amount (%)", "value": loan_pct, "color": "#0B1D51"},
            {"label": "Collateral Value (%)", "value": collateral_pct, "color": "#ffe600"},
        ],
        "caption": caption,
    }


def collateral_coverage_insight(collateral_coverage: float) -> dict:
    """Severity-tagged insight message about collateral coverage."""
    if collateral_coverage < 1:
        return {
            "level": "warning",
            "message": (
                "Collateral coverage is less than 1. This means the borrower's collateral value is "
                "lower than the loan amount, which increases the lender's risk in case of default."
            ),
        }
    if collateral_coverage == 1:
        return {
            "level": "info",
            "message": (
                "Collateral coverage is exactly 1. The collateral value matches the loan amount, "
                "offering basic security but little margin for error."
            ),
        }
    return {
        "level": "success",
        "message": (
            "Collateral coverage is greater than 1. The borrower's collateral value exceeds the loan "
            "amount, reducing risk for the lender."
        ),
    }


def build_risk_gauge(risk_score: float) -> dict:
    """
    Gauge chart data: risk score (0-100) with the same 3 colored zones used
    on the Recovery Insights dashboard border (0-35 green / 35-85 amber /
    85-100 red).
    """
    risk_pct = round(risk_score * 100, 2)
    return {
        "type": "gauge",
        "value": risk_pct,
        "zones": [
            {"range": [0, DASHBOARD_LOW_RISK_PCT], "color": "#388e3c"},
            {"range": [DASHBOARD_LOW_RISK_PCT, DASHBOARD_HIGH_RISK_PCT], "color": "#D49B54"},
            {"range": [DASHBOARD_HIGH_RISK_PCT, 100], "color": "#d32f2f"},
        ],
        "caption": (
            f"Predicted risk of default: {risk_pct:.2f}%. Higher values indicate greater likelihood "
            "of default and need for stronger recovery action."
        ),
    }


def build_analytics_bundle(
    *,
    emi_to_income_ratio: float,
    collateral_coverage: float,
    loan_tenure: int,
    missed_payments: int,
    loan_amount: float,
    collateral_value: float,
    risk_score: float,
) -> dict:
    """Assemble every chart/insight the Recovery Insights dashboard needs in one call."""
    return {
        "feature_percentage_chart": build_feature_percentage_chart(emi_to_income_ratio, collateral_coverage),
        "payment_history_chart": build_payment_history_chart(loan_tenure, missed_payments),
        "loan_vs_collateral_chart": build_loan_vs_collateral_chart(loan_amount, collateral_value),
        "collateral_coverage_insight": collateral_coverage_insight(collateral_coverage),
        "risk_gauge": build_risk_gauge(risk_score),
    }
