"""
Training pipeline for the risk model and borrower segmentation.

Design choices, each backed by the audit in docs/MODEL_CARD.md:
- Features are built with the exact functions the API uses at serve time
  (services.feature_engineering), so training and serving cannot drift.
- XGBoost with monotone constraints (domain direction per feature) and
  interaction constraints (each tree uses one feature): the model is
  additive, so every SHAP value moves in the domain-sensible direction.
- Probabilities are calibrated with isotonic regression fitted on
  out-of-fold predictions, so a 30% score means ~30% observed outcome.
- Evaluation is repeated, nested stratified CV (calibration refitted inside
  each fold) against honest baselines, not one 150-row split.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from repository.constants import MODEL_FEATURE_ORDER, SEGMENTATION_FEATURE_ORDER
from services.feature_engineering import calculate_default_severity, calculate_emi

RANDOM_STATE = 42
AT_RISK_STATUSES = ("Written Off", "Partially Recovered")

# +1: higher value can only raise risk; -1: can only lower it; 0: no domain prior.
MONOTONE_DIRECTION = {
    "Age": 0,
    "Monthly_Income": -1,
    "Num_Dependents": 1,
    "Loan_Tenure": 1,
    "Interest_Rate": 1,
    "Outstanding_Loan_Amount": 1,
    "Collection_Attempts": 1,
    "EMI_to_Income_Ratio": 1,
    "Collateral_Coverage": -1,
    "Default_Severity": 1,
}

XGB_PARAMS = {
    "n_estimators": 200,
    "max_depth": 2,
    "learning_rate": 0.05,
    "min_child_weight": 5,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "eval_metric": "logloss",
    "random_state": RANDOM_STATE,
}


def load_dataset(path) -> tuple[pd.DataFrame, np.ndarray]:
    raw = pd.read_csv(path)
    target = raw["Recovery_Status"].isin(AT_RISK_STATUSES).astype(int).to_numpy()
    return raw, target


def build_features(raw: pd.DataFrame) -> pd.DataFrame:
    """Same formulas as the API. Uses formula EMI, not the dataset's Monthly_EMI column."""
    emi = [
        calculate_emi(p, r, t) or 0.0
        for p, r, t in zip(raw["Loan_Amount"], raw["Interest_Rate"], raw["Loan_Tenure"], strict=True)
    ]
    features = pd.DataFrame(
        {
            "Age": raw["Age"],
            "Monthly_Income": raw["Monthly_Income"],
            "Num_Dependents": raw["Num_Dependents"],
            "Loan_Tenure": raw["Loan_Tenure"],
            "Interest_Rate": raw["Interest_Rate"],
            "Outstanding_Loan_Amount": raw["Outstanding_Loan_Amount"],
            "Collection_Attempts": raw["Collection_Attempts"],
            "EMI_to_Income_Ratio": np.round(np.array(emi) / raw["Monthly_Income"], 3),
            "Collateral_Coverage": np.round(raw["Collateral_Value"] / raw["Loan_Amount"], 3),
            "Default_Severity": [
                calculate_default_severity(m, d)
                for m, d in zip(raw["Num_Missed_Payments"], raw["Days_Past_Due"], strict=True)
            ],
        }
    )
    return features[MODEL_FEATURE_ORDER].astype(float)


def make_model() -> XGBClassifier:
    return XGBClassifier(
        **XGB_PARAMS,
        monotone_constraints=tuple(MONOTONE_DIRECTION[f] for f in MODEL_FEATURE_ORDER),
        interaction_constraints=[[f] for f in MODEL_FEATURE_ORDER],
    )


def _fit_calibrator(X: pd.DataFrame, y: np.ndarray, seed: int) -> IsotonicRegression:
    oof = cross_val_predict(
        make_model(), X, y, cv=StratifiedKFold(5, shuffle=True, random_state=seed), method="predict_proba"
    )[:, 1]
    return IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0).fit(oof, y)


def fit_calibrated(X: pd.DataFrame, y: np.ndarray) -> tuple[XGBClassifier, IsotonicRegression]:
    return make_model().fit(X, y), _fit_calibrator(X, y, RANDOM_STATE)


def expected_calibration_error(y: np.ndarray, p: np.ndarray, bins: int = 10) -> float:
    idx = np.minimum((p * bins).astype(int), bins - 1)
    return float(sum(abs(y[idx == b].mean() - p[idx == b].mean()) * (idx == b).mean() for b in np.unique(idx)))


def _summarise(aucs, briers, eces) -> dict:
    return {
        "roc_auc_mean": round(float(np.mean(aucs)), 4),
        "roc_auc_95pct_range": [round(float(v), 4) for v in np.percentile(aucs, [2.5, 97.5])],
        "brier_mean": round(float(np.mean(briers)), 4),
        "ece_mean": round(float(np.mean(eces)), 4),
    }


def cross_validate(X: pd.DataFrame, y: np.ndarray, repeats: int = 5) -> dict:
    """Nested repeated CV for the calibrated model plus two honest baselines."""
    results = {}
    candidates = {
        "calibrated_monotone_xgb": None,
        "baseline_logistic_collection_attempts_only": lambda: make_pipeline(StandardScaler(), LogisticRegression()),
    }
    for name, make in candidates.items():
        aucs, briers, eces = [], [], []
        for rep in range(repeats):
            p = np.zeros(len(y))
            for train, test in StratifiedKFold(5, shuffle=True, random_state=rep).split(X, y):
                if make is None:
                    model, calibrator = (
                        make_model().fit(X.iloc[train], y[train]),
                        _fit_calibrator(X.iloc[train], y[train], rep),
                    )
                    p[test] = calibrator.predict(model.predict_proba(X.iloc[test])[:, 1])
                else:
                    cols = ["Collection_Attempts"]
                    p[test] = make().fit(X.iloc[train][cols], y[train]).predict_proba(X.iloc[test][cols])[:, 1]
            aucs.append(roc_auc_score(y, p))
            briers.append(brier_score_loss(y, p))
            eces.append(expected_calibration_error(y, p))
        results[name] = _summarise(aucs, briers, eces)
    results["baseline_predict_base_rate"] = {
        "brier_mean": round(float(brier_score_loss(y, np.full(len(y), y.mean()))), 4)
    }
    return results


def feature_signal_audit(X: pd.DataFrame, y: np.ndarray) -> dict[str, float]:
    """Univariate AUC per feature (0.5 = no signal), folded so direction doesn't matter."""
    return {f: round(float(max(a, 1 - a)), 3) for f in X.columns for a in [roc_auc_score(y, X[f])]}


# (low-side phrase, high-side phrase) used to name segments by what sets them apart.
SEGMENT_TRAIT_WORDS = {
    "Age": ("Younger borrowers", "Older borrowers"),
    "Monthly_Income": ("Lower income", "Higher income"),
    "Num_Dependents": ("Fewer dependents", "More dependents"),
    "Loan_Tenure": ("Short tenure", "Long tenure"),
    "Interest_Rate": ("Low interest rate", "High interest rate"),
    "Outstanding_Loan_Amount": ("Small outstanding balance", "Large outstanding balance"),
    "Collection_Attempts": ("Few collection attempts", "Many collection attempts"),
    "EMI_to_Income_Ratio": ("Light EMI burden", "Heavy EMI burden"),
    "Collateral_Coverage": ("Thin collateral", "Strong collateral"),
    "Default_Severity": ("Mild delinquency", "Severe delinquency"),
}


def _lower_first(text: str) -> str:
    return text[0].lower() + text[1:]


def build_segments(X: pd.DataFrame, y: np.ndarray, k: int = 4):
    """KMeans segments named after the two traits that most set each apart, so names can never go stale."""
    seg_X = X[SEGMENTATION_FEATURE_ORDER]
    scaler = StandardScaler().fit(seg_X)
    kmeans = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10).fit(scaler.transform(seg_X))
    labels = kmeans.labels_

    overall_mean, overall_std = seg_X.mean(), seg_X.std()
    base_rate = y.mean()
    profiles: dict[int, dict] = {}
    for cluster in range(k):
        members = labels == cluster
        z = (seg_X.loc[members].mean() - overall_mean) / overall_std
        traits = [SEGMENT_TRAIT_WORDS[f][int(z[f] > 0)] for f in z.abs().sort_values(ascending=False).index[:2]]
        at_risk = float(y[members].mean())
        risk_word = "above" if at_risk > base_rate * 1.15 else "below" if at_risk < base_rate * 0.85 else "close to"
        income = float(seg_X.loc[members, "Monthly_Income"].median())
        burden = float(seg_X.loc[members, "EMI_to_Income_Ratio"].median())
        profiles[cluster] = {
            "name": f"{traits[0]}, {_lower_first(traits[1])}",
            "description": (
                f"What sets this group apart: {_lower_first(traits[0])} and {_lower_first(traits[1])}. "
                f"Median monthly income is "
                f"₹{income:,.0f} with an EMI-to-income ratio of {burden:.2f}. In the training data, {at_risk:.0%} of "
                f"these borrowers were not fully recovered, {risk_word} the {base_rate:.0%} portfolio average."
            ),
            "size": int(members.sum()),
            "observed_at_risk_rate": round(at_risk, 3),
        }
    names = [p["name"] for p in profiles.values()]
    for cluster, profile in profiles.items():
        if names.count(profile["name"]) > 1:
            profile["name"] = f"{profile['name']} · group {cluster + 1}"
    return scaler, kmeans, profiles
