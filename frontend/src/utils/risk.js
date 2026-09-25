/**
 * Risk display helpers. The backend owns risk tiers: every prediction
 * returns `risk_band`, so the UI colors by that and never re-derives tiers.
 *
 * `risk_score` is a calibrated probability that the loan will not be fully
 * recovered, so the gauge maps it 0-1 directly with no stretching.
 */

// Mirrors the policy cutoffs in backend/repository/constants.py. Used only
// to color a bare score that has no backend band (e.g. the hero gauge).
const MEDIUM_RISK_THRESHOLD = 0.3;
const HIGH_RISK_THRESHOLD = 0.55;
const VERY_HIGH_RISK_THRESHOLD = 0.8;

const BAND_BY_CATEGORY = {
  'Critical Risk': 'critical',
  'High Risk': 'high',
  'Medium Risk': 'medium',
  'Low Risk': 'low',
};

export function bandFromScore(riskScore) {
  if (riskScore >= VERY_HIGH_RISK_THRESHOLD) return 'critical';
  if (riskScore >= HIGH_RISK_THRESHOLD) return 'high';
  if (riskScore >= MEDIUM_RISK_THRESHOLD) return 'medium';
  return 'low';
}

/** Prefer the backend's band; fall back to its category label for rows saved before bands existed. */
export function resolveBand({ band, category, score }) {
  return band ?? BAND_BY_CATEGORY[category] ?? bandFromScore(score ?? 0);
}

export const RISK_COLORS = {
  low: 'var(--color-risk-low)',
  medium: 'var(--color-risk-medium)',
  high: 'var(--color-risk-high)',
  critical: 'var(--color-risk-critical)',
};

export function formatPercent(value, decimals = 2) {
  return `${(value * 100).toFixed(decimals)}%`;
}

export function formatCurrencyINR(value) {
  return `₹${Math.round(value).toLocaleString('en-IN')}`;
}
