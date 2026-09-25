"""
Retrain the risk model and borrower segmentation, evaluate honestly, and
save artifacts only if the new model beats the baselines.

    cd backend && python retrain.py

Writes ml_artifacts/{xgb_tuned,calibrator,scaler,kmeans,segment_profiles}.pkl,
ml_artifacts/manifest.json and metrics_report.json.
"""

import json
import pickle
import sys
from datetime import UTC, datetime
from pathlib import Path

from ml import pipeline
from scripts.write_manifest import write_manifest

BACKEND = Path(__file__).resolve().parent
DATASET = BACKEND.parent / "Dataset" / "loan-recovery.csv"
ARTIFACTS = BACKEND / "ml_artifacts"


def main() -> int:
    raw, y = pipeline.load_dataset(DATASET)
    X = pipeline.build_features(raw)
    print(f"Loaded {len(X)} rows; at-risk rate {y.mean():.3f}")

    evaluation = pipeline.cross_validate(X, y)
    model_cv = evaluation["calibrated_monotone_xgb"]
    for name, metrics in evaluation.items():
        print(f"  {name:45s} {metrics}")

    baselines = [evaluation["baseline_logistic_collection_attempts_only"], evaluation["baseline_predict_base_rate"]]
    if any(model_cv["brier_mean"] >= b["brier_mean"] for b in baselines):
        print("REJECTED: calibrated model does not beat the baselines on Brier score; artifacts left unchanged.")
        return 1

    model, calibrator = pipeline.fit_calibrated(X, y)
    scaler, kmeans, segment_profiles = pipeline.build_segments(X, y)
    for cluster, profile in segment_profiles.items():
        rate = profile["observed_at_risk_rate"]
        print(f"  segment {cluster}: {profile['name']} (n={profile['size']}, at-risk {rate:.0%})")

    for name, obj in {
        "xgb_tuned.pkl": model,
        "calibrator.pkl": calibrator,
        "scaler.pkl": scaler,
        "kmeans.pkl": kmeans,
        "segment_profiles.pkl": segment_profiles,
    }.items():
        with open(ARTIFACTS / name, "wb") as f:
            pickle.dump(obj, f)

    report = {
        "trained_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "dataset_rows": len(X),
        "target": f"1 if Recovery_Status in {list(pipeline.AT_RISK_STATUSES)} else 0",
        "positive_rate": round(float(y.mean()), 4),
        "evaluation": "5x repeated stratified 5-fold CV; calibration refitted inside each fold",
        "cross_validation": evaluation,
        "univariate_feature_auc": pipeline.feature_signal_audit(X, y),
        "model": {"xgboost_params": pipeline.XGB_PARAMS, "monotone_direction": pipeline.MONOTONE_DIRECTION},
        "segments": segment_profiles,
    }
    (BACKEND / "metrics_report.json").write_text(json.dumps(report, indent=2) + "\n")
    for digest_name, digest in write_manifest().items():
        print(f"  {digest[:12]}  {digest_name}")
    print("Saved artifacts, metrics_report.json and manifest.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
