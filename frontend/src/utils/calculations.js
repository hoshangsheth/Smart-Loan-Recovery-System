/**
 * Client-side preview calculations, mirroring
 * backend/services/feature_engineering.py exactly. These are used only to
 * give the user live feedback (EMI, DPD, collection attempts) as they fill
 * the form — the backend independently recomputes everything during
 * prediction, so there's no risk of these two ever silently diverging in
 * a way that affects the actual result.
 */

export function calculateEmi(principal, annualRate, tenureMonths) {
  if (!principal || !annualRate || !tenureMonths) return null;
  const r = annualRate / (12 * 100);
  const emi = (principal * r * Math.pow(1 + r, tenureMonths)) / (Math.pow(1 + r, tenureMonths) - 1);
  return Math.round(emi * 100) / 100;
}

export function calculateDaysPastDue(missedPayments) {
  return (missedPayments || 0) * 30;
}

export function calculateCollectionAttempts(missedPayments, daysPastDue) {
  if (!missedPayments) return 0;
  if (daysPastDue <= 30) return 1;
  if (daysPastDue <= 60) return 2;
  if (daysPastDue <= 90) return 3;
  return 4;
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
