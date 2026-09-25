import { supabase } from '../lib/supabase';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

class ApiError extends Error {
  constructor(message, status, details) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

async function authHeader() {
  if (!supabase) return {};
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(await authHeader()) },
  });

  if (!res.ok) {
    let details = null;
    try {
      details = await res.json();
    } catch {
      // response had no JSON body
    }
    throw new ApiError(
      typeof details?.detail === 'string'
        ? details.detail
        : details?.detail?.message
          ? details.detail.message
          : details?.detail
            ? JSON.stringify(details.detail)
            : `Request failed (${res.status})`,
      res.status,
      details
    );
  }
  return res;
}

/** Run the full risk prediction pipeline for one borrower. */
export async function predictRisk(borrowerInput) {
  const res = await request('/predict', {
    method: 'POST',
    body: JSON.stringify(borrowerInput),
  });
  return res.json();
}

/** Fetch chart-ready analytics for the Recovery Insights dashboard. */
export async function getAnalytics(analyticsInput) {
  const res = await request('/analytics', {
    method: 'POST',
    body: JSON.stringify(analyticsInput),
  });
  return res.json();
}

/** Download the borrower's PDF report as a Blob. */
export async function downloadReport(reportInput) {
  const res = await request('/report', {
    method: 'POST',
    body: JSON.stringify(reportInput),
  });
  return res.blob();
}

/** Get the configured WhatsApp contact link. */
export async function getWhatsAppLink() {
  const res = await request('/contact/whatsapp-link');
  return res.json();
}

/** Case queue for the signed-in officer, highest current risk first. */
export async function listCases(status) {
  const query = status ? `?status=${encodeURIComponent(status)}` : '';
  const res = await request(`/cases${query}`);
  return res.json();
}

export async function getCase(caseId) {
  const res = await request(`/cases/${encodeURIComponent(caseId)}`);
  return res.json();
}

export async function updateCaseStatus(caseId, status) {
  const res = await request(`/cases/${encodeURIComponent(caseId)}`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
  return res.json();
}

/** Ask Gemini for a structured case brief. Takes several seconds. */
export async function generateCaseBrief(caseId) {
  const res = await request(`/cases/${encodeURIComponent(caseId)}/brief`, { method: 'POST' });
  return res.json();
}

/** Consent status and AI brief allowance for the signed-in user. */
export async function getMe() {
  const res = await request('/me');
  return res.json();
}

export async function acceptTerms(termsVersion) {
  const res = await request('/me/consent', {
    method: 'POST',
    body: JSON.stringify({ terms_version: termsVersion }),
  });
  return res.json();
}

export { ApiError };
