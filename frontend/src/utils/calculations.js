/**
 * Client-side preview calculations, mirroring
 * backend/services/feature_engineering.py exactly. These are used only to
 * give the user live feedback (EMI) as they fill the form — the backend
 * independently recomputes everything during prediction, so there's no
 * risk of these two ever silently diverging in a way that affects the
 * actual result.
 *
 * `calculateDaysPastDue()` and `calculateCollectionAttempts()` used to
 * live here, deriving both values from `missed_payments` via a formula and
 * a step function capped at 4. They're removed: the training data shows
 * Collection_Attempts is essentially uncorrelated with missed payments or
 * DPD (r ~= 0.03-0.06) despite being the model's single strongest feature
 * (~63% importance), and real DPD isn't a clean multiple of missed
 * payments either (r ~= 0.34). Both are now collected as direct inputs
 * from the recovery officer in BorrowerForm — see the "Days Past Due" and
 * "Collection Attempts" fields there.
 */

export function calculateEmi(principal, annualRate, tenureMonths) {
  if (!principal || !annualRate || !tenureMonths) return null;
  const r = annualRate / (12 * 100);
  const emi = (principal * r * Math.pow(1 + r, tenureMonths)) / (Math.pow(1 + r, tenureMonths) - 1);
  return Math.round(emi * 100) / 100;
}

export function calculateEmiToIncome(monthlyEmi, monthlyIncome) {
  if (!monthlyIncome || !monthlyEmi) return null;
  return Math.round((monthlyEmi / monthlyIncome) * 1000) / 1000;
}

export function calculateCollateralCoverage(collateralValue, loanAmount) {
  if (!loanAmount || collateralValue == null) return null;
  return Math.round((collateralValue / loanAmount) * 1000) / 1000;
}

export function calculateDefaultSeverity(missedPayments, daysPastDue) {
  return (missedPayments || 0) * (daysPastDue || 0);
}
