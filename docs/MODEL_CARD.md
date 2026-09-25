# Model card: Recovia risk model

## What it predicts
`risk_score` is the **calibrated probability that a loan will not be fully recovered**. Positive outcomes are `Recovery_Status` of *Written Off* or *Partially Recovered*. Because the score is calibrated, 30% means roughly 30 of 100 similar borrowers were not fully recovered.

## Data
- 500 synthetic borrower records (`Dataset/loan-recovery.csv`). 40.8% of them are positive.
- **Signal audit.** This is univariate AUC, where 0.5 means no signal.

| Feature | AUC |
|---|---|
| Collection_Attempts | **0.787** |
| All other nine model features | 0.50–0.54 |
| Unused categoricals (Payment_History, Employment_Type, Loan_Type) | no signal (0.49 in CV) |

- The outcome follows a near-deterministic rule: **4 or more collection attempts means 100% positive**. Borrowers with 0–3 attempts are positive about 21% of the time, and within that group no other feature predicts better than chance (CV AUC 0.51–0.53).
- `Legal_Action_Taken` is excluded because it only happens after the outcome is known (100% positive when "Yes"), so using it would leak the answer into the model.

**What this means:** this model is only as good as its training data. It can't learn that days past due or missed payments matter, because in this dataset they don't. Real delinquency is handled by the policy layer below until the model is retrained on real outcomes.

## Model
- **XGBoost** with `max_depth=2`, 200 trees and learning rate 0.05.
- **Monotone constraints** force each feature's direction:
  - Risk can only rise with collection attempts, default severity, EMI-to-income, outstanding amount, dependents, interest rate and tenure.
  - Risk can only fall with income and collateral coverage.
  - Age is left unconstrained.
- **Interaction constraints** limit each tree to one feature, so the model is additive and every SHAP value points in the domain direction.
- **Isotonic calibration** is fitted on out-of-fold predictions. Scores are clipped to [0.02, 0.98], because 500 rows can't justify certainty either way.
- **Training/serving parity.** Features are built with the same functions the API uses. EMI comes from the reducing-balance formula; the dataset's own `Monthly_EMI` column is ignored because it runs at a median 43% of the formula value.

## Evaluation
5× repeated stratified 5-fold cross-validation, with calibration refitted inside each fold:

| Model | ROC-AUC (95% range) | Brier ↓ | Calibration error (ECE) ↓ |
|---|---|---|---|
| **This model** | **0.805** (0.794–0.811) | **0.126** | **0.021** |
| Logistic regression on collection attempts only | 0.781 | 0.152 | 0.158 |
| Always predict the base rate | 0.500 | 0.242 | — |
| Previous model (unconstrained, uncalibrated) | 0.821 | 0.146 | 0.103 |

The previous model had 0.016 higher AUC. That gap came from fitting a dip in which 1 collection attempt looked riskier than 2, and from noise in the other features. It also produced explanations that pointed the wrong way (for example "severity decreased risk") and probabilities that were off by 10 points on average. `retrain.py` refuses to save any model that doesn't beat both baselines on Brier score, and the tests re-check this against `metrics_report.json`.

## Policy layer (outside the model)
- **Asset class** follows RBI's early-stress classification by days past due: Standard (0), SMA-0 (1–30), SMA-1 (31–60), SMA-2 (61–90) and NPA (more than 90).
- **Tier = the higher of the model tier and the policy floor.**
  - Model tiers: Low below 30%, Medium 30–55%, High 55–80%, Very High 80% and above.
  - Policy floors: an NPA account is at least High, and an SMA-2 account is at least Medium.
- **Critical** requires a model score of at least 80% *and* an NPA account. If the score is at least 80% but the account isn't NPA yet, the tier is High, with a warning that it becomes Critical after 90 days past due.
- When a policy floor raises the tier, the response says so in `policy_override`.

## Segments
KMeans with k=4 on the same 10 features. Each segment is **named from the two traits that most set it apart** (standardized difference from the portfolio mean), and its description reports its observed at-risk rate. Names are regenerated on every retrain, so they can't go stale. On this data, every segment's at-risk rate is close to the portfolio average (37–46%). Segments describe borrower profiles, not risk.

## Guarantees enforced by tests (`tests/test_model_behaviour.py`)
- Risk never falls as collection attempts, days past due, missed payments, outstanding amount or dependents grow.
- Risk never rises as collateral or income grows.
- Scores stay within [0.02, 0.98].
- For a heavily delinquent borrower, the explanations for collection attempts and default severity always point to *increased* risk.
- An NPA borrower is never Low Risk.
- The saved model beats both baselines, with calibration error below 0.05.

## Retraining
`cd backend && python retrain.py`. Running it twice produces identical model, calibrator and segment artifacts.
