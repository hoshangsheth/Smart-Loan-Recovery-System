/**
 * Risk band + color helpers, mirroring the backend's threshold schemes.
 *
 * The original app (and this refactor) intentionally keeps THREE separate
 * threshold schemes — see backend/repository/constants.py for why. This
 * file is the frontend's single source of truth for all three, so no
 * component invents its own cutoffs.
 *
 * RECALIBRATED July 2026 to match backend/repository/constants.py after
 * retraining the model on real Recovery_Status outcomes (previously
 * trained on a circular cluster-derived label). The new model's honest
 * predict_proba output only spans ~0.20-0.75 on this dataset — these
 * cutoffs are set relative to that actual range, not the old 0-1 tail
 * values. If the model is retrained again, re-check these against the new
 * probability distribution.
 */

// Scheme 1: predictor results card + PDF (3-band).
export function getDisplayRiskBand(riskScore) {
  if (riskScore > 0.65) return 'high';
  if (riskScore > 0.32) return 'medium';
  return 'low';
}

// Scheme 2: Recovery Insights dashboard accent/border + gauge zones (3-band,
// percentage cutoffs: <32 / 32-65 / >65).
export function getDashboardRiskBand(riskScore) {
  const pct = riskScore * 100;
  if (pct < 32) return 'low';
  if (pct <= 65) return 'medium';
  return 'high';
}

// "Approaching critical zone" warning band (65-72%).
export function isApproachingCriticalZone(riskScore) {
  const pct = riskScore * 100;
  return pct >= 65 && pct < 72;
}

// The model's actual observed predict_proba range on this dataset. Used
// purely for VISUAL scaling (the gauge arc, chart axes) so a "safe"
// borrower's gauge reads near-empty and a "critical" borrower's gauge reads
// near-full, instead of every borrower being compressed into the same
// 20-75% slice of a raw 0-1 arc. The displayed numeric percentage always
// shows the true, unscaled risk score — only the arc FILL is stretched.
export const MODEL_SCORE_MIN = 0.18;
export const MODEL_SCORE_MAX = 0.78;

export function normalizeForGauge(riskScore) {
  const clamped = Math.min(Math.max(riskScore, MODEL_SCORE_MIN), MODEL_SCORE_MAX);
  return (clamped - MODEL_SCORE_MIN) / (MODEL_SCORE_MAX - MODEL_SCORE_MIN);
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
