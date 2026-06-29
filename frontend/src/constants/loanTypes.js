/**
 * Mirrors backend/repository/constants.py LOAN_TYPE_DEFAULTS exactly.
 * Used only to show the "typical terms" hint instantly in the UI before
 * submission — the backend remains the source of truth for the actual
 * defaults applied during prediction.
 */
export const LOAN_TYPE_DEFAULTS = {
  Personal: { interestRate: 14.0, tenure: 48 },
  Auto: { interestRate: 10.5, tenure: 60 },
  Business: { interestRate: 16.0, tenure: 36 },
  Home: { interestRate: 9.0, tenure: 180 },
};

export const LOAN_TYPES = ['Personal', 'Auto', 'Business', 'Home'];
