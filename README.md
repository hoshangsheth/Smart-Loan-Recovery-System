# Smart Loan Recovery System — FastAPI + React Refactor

Two folders, two deployments:

- `backend/` — FastAPI API (deploy to Render)
- `frontend/` — Vite + React app (deploy to Vercel)

## Local development

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        # Windows; use `cp` on macOS/Linux
uvicorn main:app --reload --port 8000
```
Visit `http://localhost:8000/docs` for interactive API docs.

**Frontend**
```bash
cd frontend
npm install
copy .env.example .env        # Windows; use `cp` on macOS/Linux
npm run dev
```
Visit `http://localhost:5173`.

Make sure the backend is running first — the frontend calls
`http://localhost:8000/api/v1` by default (set in `frontend/.env`).

## Deploying

**Backend → Render**
1. Push `backend/` to a GitHub repo (or connect this folder as the root if monorepo).
2. In Render: New → Web Service → connect the repo → it will detect `render.yaml`/`Dockerfile` automatically.
3. Set `CORS_ALLOWED_ORIGINS` env var to your real Vercel URL once you have it.
4. Free tier note: the service spins down when idle, so the first request after a period of inactivity will be slow while it loads the ML artifacts again — this is expected.

**Frontend → Vercel**
1. Push `frontend/` to a GitHub repo.
2. In Vercel: New Project → import the repo → framework auto-detected as Vite (uses `vercel.json`).
3. Set the env var `VITE_API_BASE_URL` to your Render backend URL + `/api/v1`, e.g.
   `https://slrs-backend.onrender.com/api/v1`.
4. Redeploy after setting the env var (Vercel only bakes env vars in at build time).

## What changed vs. the original Streamlit app

- Same model (`xgb_tuned.pkl`), same 10-feature input order, same EMI/DPD/strategy logic — ported exactly, not re-trained.
- Borrower segmentation (previously unused `scaler.pkl`/`kmeans.pkl`) is now a live feature, shown on the dashboard and in the PDF.
- Contact form (Google Sheets) replaced with a direct WhatsApp link.
- SHAP waterfall image replaced with an equivalent interactive chart (same values, rendered client-side).
- Charts (bar/donut/pie/gauge) are now React/Recharts components fed by backend JSON, instead of server-rendered Plotly figures.

## Known follow-ups

- Run a manual click-through of the Predictor → Dashboard flow once deployed (the automated browser test was interrupted mid-session due to sandbox constraints — the individual pieces are verified working via direct API calls and screenshots, but the full click path wasn't re-confirmed after the last edit).
- Consider code-splitting the frontend bundle (currently ~770KB; Vite will warn about this on build — not an error, just a perf opportunity).
