"""Guarantees the risk model must keep across retrains."""

import json
from pathlib import Path

import pytest

from api.schemas.borrower import BorrowerInput
from models.loader import get_ml_artifacts
from repository.constants import RISK_SCORE_BOUNDS
from services.scoring_service import score_borrower

BASE = {
    "first_name": "Test",
    "last_name": "Borrower",
    "gender": "Male",
    "age": 40,
    "monthly_income": 60000,
    "num_dependents": 1,
    "loan_type": "Personal",
    "loan_amount": 500000,
    "collateral_value": 200000,
    "outstanding_loan": 300000,
    "missed_payments": 2,
    "days_past_due": 30,
    "collection_attempts": 2,
}


def score(**overrides) -> float:
    return score_borrower(BorrowerInput(**{**BASE, **overrides}), get_ml_artifacts()).risk_score


@pytest.mark.parametrize(
    ("field", "values"),
    [
        ("collection_attempts", range(0, 11)),
        ("days_past_due", [0, 30, 60, 90, 180, 365, 720]),
        ("missed_payments", range(0, 13)),
        ("outstanding_loan", [0, 100000, 300000, 600000, 1000000]),
        ("num_dependents", range(0, 6)),
    ],
)
def test_risk_never_falls_as_risk_factors_grow(field, values):
    scores = [score(**{field: v}) for v in values]
    assert scores == sorted(scores), f"{field}: {scores}"


@pytest.mark.parametrize(
    ("field", "values"),
    [("collateral_value", [0, 100000, 500000, 1000000, 2000000]), ("monthly_income", [15000, 40000, 80000, 200000])],
)
def test_risk_never_rises_as_protective_factors_grow(field, values):
    scores = [score(**{field: v}) for v in values]
    assert scores == sorted(scores, reverse=True), f"{field}: {scores}"


def test_scores_stay_within_bounds():
    for attempts in (0, 10):
        assert RISK_SCORE_BOUNDS[0] <= score(collection_attempts=attempts) <= RISK_SCORE_BOUNDS[1]


def test_explanations_point_the_domain_direction():
    result = score_borrower(
        BorrowerInput(**{**BASE, "collection_attempts": 9, "missed_payments": 12, "days_past_due": 365}),
        get_ml_artifacts(),
    )
    for feature in result.shap_top_features:
        if feature.feature in {"Collection Attempts", "Default Severity"}:
            assert feature.direction == "increased", feature


def test_npa_borrower_is_never_low_risk_even_when_model_is_low():
    result = score_borrower(
        BorrowerInput(**{**BASE, "collection_attempts": 0, "days_past_due": 365}), get_ml_artifacts()
    )
    assert result.asset_classification == "NPA"
    assert result.risk_tier in {"high", "critical"}


def test_saved_model_beats_baselines():
    report = json.loads((Path(__file__).resolve().parent.parent / "metrics_report.json").read_text())
    cv = report["cross_validation"]
    model = cv["calibrated_monotone_xgb"]
    assert model["brier_mean"] < cv["baseline_logistic_collection_attempts_only"]["brier_mean"]
    assert model["brier_mean"] < cv["baseline_predict_base_rate"]["brier_mean"]
    assert model["ece_mean"] < 0.05
