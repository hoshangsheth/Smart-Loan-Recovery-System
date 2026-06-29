/**
 * Risk band + color helpers, mirroring the backend's threshold schemes.
 *
 * The original app (and this refactor) intentionally keeps THREE separate
 * threshold schemes — see backend/repository/constants.py for why. This
 * file is the frontend's single source of truth for all three, so no
 * component invents its own cutoffs.
 */

// Scheme 1: predictor results card + PDF (3-band).
export function getDisplayRiskBand(riskScore) {
  if (riskScore > 0.75) return 'high';
  if (riskScore > 0.25) return 'medium';
  return 'low';
}

// Scheme 2: Recovery Insights dashboard accent/border + gauge zones (3-band,
// percentage cutoffs: <35 / 35-85 / >85).
export function getDashboardRiskBand(riskScore) {
  const pct = riskScore * 100;
  if (pct < 35) return 'low';
  if (pct <= 85) return 'medium';
  return 'high';
}

// "Approaching critical zone" warning band (80-85%).
export function isApproachingCriticalZone(riskScore) {
  const pct = riskScore * 100;
  return pct >= 80 && pct < 85;
}

export const RISK_COLORS = {
  low: 'var(--color-risk-low)',
  medium: 'var(--color-risk-medium)',
  high: 'var(--color-risk-high)',
};

export const RISK_LABELS = {
  low: 'Low Risk',
  medium: 'Medium Risk',
  high: 'High Risk',
};

export function formatPercent(value, decimals = 2) {
  return `${(value * 100).toFixed(decimals)}%`;
}

export function formatCurrencyINR(value) {
  return `₹${Math.round(value).toLocaleString('en-IN')}`;
}
