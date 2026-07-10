"""
Recovia retrain.py — proper retraining using REAL loan outcomes.

Fixes the circularity bug in the original notebook: the old model was trained
to predict `High_Risk_Flag`, a label manually derived from KMeans clusters
built on the same features used to train the classifier. This version trains
against `Recovery_Status`, the actual observed loan outcome, so the model
predicts real defaults/recovery failure instead of reconstructing its own
clustering rule.
"""
import pickle
import json

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    accuracy_score, precision_score, recall_score, f1_score
)
from xgboost import XGBClassifier

RANDOM_STATE = 42

# ---------------------------------------------------------------
# 1. Load raw data
# ---------------------------------------------------------------
df = pd.read_csv("../Dataset/loan-recovery.csv")
print(f"Loaded {df.shape[0]} rows, {df.shape[1]} columns")

# ---------------------------------------------------------------
# 2. Feature engineering — identical formulas to original notebook
# ---------------------------------------------------------------
df["EMI_to_Income_Ratio"] = df["Monthly_EMI"] / df["Monthly_Income"]
df["Collateral_Coverage"] = df["Collateral_Value"] / df["Loan_Amount"]
df["Default_Severity"] = df["Num_Missed_Payments"] * df["Days_Past_Due"]

FEATURES = [
    "Age", "Monthly_Income", "Num_Dependents", "Loan_Tenure", "Interest_Rate",
    "Outstanding_Loan_Amount", "Collection_Attempts",
    "EMI_to_Income_Ratio", "Collateral_Coverage", "Default_Severity",
]

# ---------------------------------------------------------------
# 3. REAL target — collapse actual Recovery_Status into binary
#    1 = at-risk (Written Off or Partially Recovered)
#    0 = Fully Recovered
# ---------------------------------------------------------------
print("\nRecovery_Status distribution:")
print(df["Recovery_Status"].value_counts())

df["At_Risk"] = df["Recovery_Status"].apply(
    lambda s: 1 if s in ("Written Off", "Partially Recovered") else 0
)
print(f"\nBinary target balance: {df['At_Risk'].value_counts().to_dict()}")
print(f"Positive rate: {df['At_Risk'].mean():.3f}")

# ---------------------------------------------------------------
# 4. Train/test split — same methodology as original (70/30, seed 42)
# ---------------------------------------------------------------
train_data, test_data = train_test_split(
    df, test_size=0.3, random_state=RANDOM_STATE, stratify=df["At_Risk"]
)

# Further split train into train/valid (80/20, stratified) — same as original
X = train_data[FEATURES]
y = train_data["At_Risk"]
X_train, X_valid, y_train, y_valid = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)

print(f"\nTrain: {len(X_train)} | Valid: {len(X_valid)} | Test: {len(test_data)}")

# ---------------------------------------------------------------
# 5. Baseline XGBoost
# ---------------------------------------------------------------
xgb_base = XGBClassifier(random_state=RANDOM_STATE, eval_metric="logloss")
xgb_base.fit(X_train, y_train)

y_pred_base = xgb_base.predict(X_valid)
y_proba_base = xgb_base.predict_proba(X_valid)[:, 1]

print("\n=== Baseline XGBoost — Validation ===")
print(confusion_matrix(y_valid, y_pred_base))
print(classification_report(y_valid, y_pred_base))
print(f"ROC AUC: {roc_auc_score(y_valid, y_proba_base):.4f}")

# ---------------------------------------------------------------
# 6. Hyperparameter tuning (same search space as original notebook)
# ---------------------------------------------------------------
xgb_param_grid = {
    "n_estimators": [100, 200, 300],
    "max_depth": [3, 5, 7, 10],
    "learning_rate": [0.01, 0.05, 0.1, 0.2],
    "subsample": [0.7, 0.8, 1.0],
    "colsample_bytree": [0.7, 0.8, 1.0],
}

cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)
xgb_search = RandomizedSearchCV(
    XGBClassifier(random_state=RANDOM_STATE, eval_metric="logloss"),
    xgb_param_grid, n_iter=15, scoring="roc_auc", cv=cv,
    n_jobs=-1, random_state=RANDOM_STATE,
)
xgb_search.fit(X_train, y_train)
best_xgb = xgb_search.best_estimator_
print(f"\nBest params: {xgb_search.best_params_}")

# ---------------------------------------------------------------
# 7. Final evaluation — validation AND held-out test set
# ---------------------------------------------------------------
def evaluate(model, X_, y_, label):
    pred = model.predict(X_)
    proba = model.predict_proba(X_)[:, 1]
    print(f"\n=== Tuned XGBoost — {label} ===")
    print(confusion_matrix(y_, pred))
    print(classification_report(y_, pred))
    auc = roc_auc_score(y_, proba)
    print(f"ROC AUC: {auc:.4f}")
    return {
        "accuracy": accuracy_score(y_, pred),
        "precision": precision_score(y_, pred),
        "recall": recall_score(y_, pred),
        "f1": f1_score(y_, pred),
        "roc_auc": auc,
        "n": len(y_),
    }

valid_metrics = evaluate(best_xgb, X_valid, y_valid, "Validation")
test_metrics = evaluate(best_xgb, test_data[FEATURES], test_data["At_Risk"], "Held-Out Test")

# ---------------------------------------------------------------
# 8. Retrain KMeans segmentation (unsupervised — no ground truth needed,
#    this part of the original pipeline was NOT circular, kept as-is
#    but retrained on the new train split for consistency)
# ---------------------------------------------------------------
scaler = StandardScaler()
train_scaled = scaler.fit_transform(train_data[FEATURES])
kmeans = KMeans(n_clusters=4, random_state=RANDOM_STATE, n_init=10)
train_data = train_data.copy()
train_data["Borrower_Segment"] = kmeans.fit_predict(train_scaled)

segment_profile = train_data.groupby("Borrower_Segment")[FEATURES].mean().round(2)
print("\n=== Segment profiles (for manual naming) ===")
print(segment_profile)

# ---------------------------------------------------------------
# 9. Save artifacts
# ---------------------------------------------------------------
with open("ml_artifacts/xgb_tuned.pkl", "wb") as f:
    pickle.dump(best_xgb, f)

with open("ml_artifacts/scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

with open("ml_artifacts/kmeans.pkl", "wb") as f:
    pickle.dump(kmeans, f)

with open("ml_artifacts/features.pkl", "wb") as f:
    pickle.dump(FEATURES, f)

with open("metrics_report.json", "w") as f:
    json.dump({"validation": valid_metrics, "test": test_metrics}, f, indent=2)

print("\nSaved: xgb_tuned.pkl, scaler.pkl, kmeans.pkl, features.pkl, metrics_report.json")
