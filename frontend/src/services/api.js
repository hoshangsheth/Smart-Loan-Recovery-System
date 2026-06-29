const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

class ApiError extends Error {
  constructor(message, status, details) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!res.ok) {
    let details = null;
    try {
      details = await res.json();
    } catch {
      // response had no JSON body
    }
    throw new ApiError(
      details?.detail ? JSON.stringify(details.detail) : `Request failed (${res.status})`,
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

export { ApiError };
