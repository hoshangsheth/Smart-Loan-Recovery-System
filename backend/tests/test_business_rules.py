import json

import pytest

from config.settings import normalize_database_url, settings
from models import loader
from services.feature_engineering import calculate_emi, engineer_features
from services.prediction_service import assign_recovery_strategy, get_display_risk_band


def test_emi_matches_reducing_balance_formula():
    assert calculate_emi(100_000, 12, 12) == pytest.approx(8884.88, abs=0.01)


def test_emi_guard_returns_none_on_zero_inputs():
    assert calculate_emi(0, 12, 12) is None
    assert calculate_emi(100_000, 0, 12) is None


def test_engineer_features_falls_back_to_loan_type_defaults():
    f = engineer_features(
        loan_type="Home", loan_amount=1_000_000, collateral_value=1_500_000, monthly_income=100_000,
        missed_payments=2, days_past_due=45, collection_attempts=1, interest_rate=None, loan_tenure=None,
    )
    assert (f.interest_rate_used, f.loan_tenure_used) == (9.0, 180)
    assert f.collateral_coverage == 1.5
    assert f.default_severity == 90


@pytest.mark.parametrize(
    ("score", "dpd", "label"),
    [
        (0.80, 90, "Critical Risk"),
        (0.80, 30, "High Risk"),
        (0.70, 120, "High Risk"),
        (0.50, 0, "Medium Risk"),
        (0.10, 200, "Low Risk"),
    ],
)
def test_strategy_tiers(score, dpd, label):
    assert assign_recovery_strategy(score, dpd)["label"] == label


def test_critical_requires_dpd_threshold_inclusive():
    assert assign_recovery_strategy(0.73, 90)["label"] == "Critical Risk"
    assert assign_recovery_strategy(0.73, 89)["label"] == "High Risk"


def test_display_bands():
    assert [get_display_risk_band(s) for s in (0.9, 0.5, 0.1)] == ["high", "medium", "low"]


def test_tampered_artifact_is_refused(tmp_path, monkeypatch):
    manifest = json.loads(settings.artifact_manifest_path.read_text())
    manifest["sha256"]["xgb_tuned.pkl"] = "0" * 64
    bad = tmp_path / "manifest.json"
    bad.write_text(json.dumps(manifest))
    monkeypatch.setattr(settings, "artifact_manifest_path", bad)
    loader.get_ml_artifacts.cache_clear()
    try:
        with pytest.raises(loader.ArtifactIntegrityError):
            loader.get_ml_artifacts()
    finally:
        loader.get_ml_artifacts.cache_clear()


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            "postgresql://postgres.abc:p@ss#w/rd@aws-0-ap-south-1.pooler.supabase.com:5432/postgres",
            "postgresql+psycopg://postgres.abc:p%40ss%23w%2Frd@aws-0-ap-south-1.pooler.supabase.com:5432/postgres",
        ),
        (
            "  postgres://postgres.abc:[secret]@host:5432/postgres\n",
            "postgresql+psycopg://postgres.abc:secret@host:5432/postgres",
        ),
        (
            "postgresql+psycopg://postgres.abc:already%40encoded@host:5432/postgres",
            "postgresql+psycopg://postgres.abc:already%40encoded@host:5432/postgres",
        ),
        ("sqlite:///./recovia.db", "sqlite:///./recovia.db"),
    ],
)
def test_database_url_accepts_supabase_dashboard_format(raw, expected):
    assert normalize_database_url(raw) == expected
