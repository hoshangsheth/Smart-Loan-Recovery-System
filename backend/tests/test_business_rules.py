import json

import pytest

from config.settings import normalize_database_url, settings
from models import loader
from services.feature_engineering import calculate_emi, engineer_features
from services.prediction_service import assess_risk, classify_asset


def test_emi_matches_reducing_balance_formula():
    assert calculate_emi(100_000, 12, 12) == pytest.approx(8884.88, abs=0.01)


def test_emi_guard_returns_none_on_zero_inputs():
    assert calculate_emi(0, 12, 12) is None
    assert calculate_emi(100_000, 0, 12) is None


def test_engineer_features_falls_back_to_loan_type_defaults():
    f = engineer_features(
        loan_type="Home",
        loan_amount=1_000_000,
        collateral_value=1_500_000,
        monthly_income=100_000,
        missed_payments=2,
        days_past_due=45,
        collection_attempts=1,
        interest_rate=None,
        loan_tenure=None,
    )
    assert (f.interest_rate_used, f.loan_tenure_used) == (9.0, 180)
    assert f.collateral_coverage == 1.5
    assert f.default_severity == 90


@pytest.mark.parametrize(
    ("dpd", "asset_class"),
    [
        (0, "Standard"),
        (1, "SMA-0"),
        (30, "SMA-0"),
        (31, "SMA-1"),
        (60, "SMA-1"),
        (61, "SMA-2"),
        (90, "SMA-2"),
        (91, "NPA"),
    ],
)
def test_rbi_asset_classification_boundaries(dpd, asset_class):
    assert classify_asset(dpd) == asset_class


@pytest.mark.parametrize(
    ("score", "dpd", "tier", "overridden"),
    [
        (0.10, 0, "low", False),
        (0.40, 0, "medium", False),
        (0.60, 0, "high", False),
        (0.90, 90, "high_no_dpd", False),
        (0.90, 91, "critical", False),
        (0.10, 75, "medium", True),
        (0.10, 120, "high", True),
        (0.60, 120, "high", False),
    ],
)
def test_tier_is_max_of_model_and_policy_floor(score, dpd, tier, overridden):
    assessment = assess_risk(score, dpd)
    assert assessment.tier == tier
    assert (assessment.policy_override is not None) == overridden


def test_critical_requires_npa():
    assert assess_risk(0.98, 90).tier == "high_no_dpd"
    assert assess_risk(0.98, 90).warning
    assert assess_risk(0.98, 91).tier == "critical"


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
