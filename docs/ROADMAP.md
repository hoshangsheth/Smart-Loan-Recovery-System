# Recovia: ML → AI MVP Roadmap

Goal: take Recovia from a stateless ML scoring demo to an MVP-grade AI
application a recovery team could actually work in. Everything runs on free
tiers except the Gemini API (paid key).

## Stack decisions

| Concern | Choice | Free-tier limit that matters |
|---|---|---|
| Database | Supabase Postgres (via SQLAlchemy + Alembic) | 500 MB DB; **project pauses after 7 days of no activity** |
| Auth | Supabase Auth (JWT verified in FastAPI) | 50k MAU |
| Vector store (Phase 4) | pgvector in the same Supabase DB | Shares the 500 MB |
| LLM | Gemini Flash (`GEMINI_MODEL`, default `gemini-3.8-flash`) | Paid. 3.6/3.7/3.8 Flash cost the same until 2026-12-31, then double |
| Backend hosting | Render free web service (Docker) | **Sleeps after 15 min idle**, ~50 s cold start, 512 MB RAM |
| Frontend hosting | Vercel Hobby | Non-commercial use only |
| CI / cron | GitHub Actions | Free minutes are plenty for this repo |

Free-tier risks and how they're handled:
- **Supabase pausing**: `keepalive.yml` hits `/health/ready` (runs `SELECT 1`) daily.
- **Render cold starts**: accepted for the MVP. The first request after idle is slow. Moving to a $7 plan removes it. Pinging to keep it warm works but uses up the 750 free instance-hours.
- **Vercel Hobby is non-commercial**: fine for a portfolio. A paying lender means moving to Pro.

## Phases

### Phase 0: Hygiene and safety net ✅
- Untrack committed `__pycache__/` files.
- pytest suite for the pure business rules (feature engineering, strategy tiers) and the API.
- GitHub Actions CI: lint (ruff) and tests on every push/PR.
- ML artifact integrity: `ml_artifacts/manifest.json` holds SHA-256 hashes. The loader refuses tampered pickles and exposes a `model_version`. `retrain.py` regenerates the manifest.

### Phase 1: Persistence ✅
- Tables: `cases`, `predictions` (full history per case, stamped with `model_version`), `case_briefs`, `audit_log`.
- Alembic migrations. RLS enabled on every table with no policies, so the Supabase anon key (which ships in the frontend) can't read borrower PII through PostgREST. Only the backend's direct DB connection can.
- `/health/ready` checks the DB.

### Phase 2: Auth ✅
- ✅ FastAPI verifies Supabase JWTs (JWKS for asymmetric keys, or the legacy HS256 secret).
- ✅ Anyone can sign up, so non-admin users are capped at `BRIEF_DAILY_LIMIT_PER_USER` Gemini briefs per rolling 24 hours (default 20) to protect the paid API key.
- ✅ Roles come from `app_metadata.role` (`officer` default, `admin` sees all cases).
- ✅ `/predict` still works anonymously but persists nothing. Signed in, it creates a case. `/cases/*` requires auth.
- ✅ Frontend: open sign-up (email + password with confirmation, and Google when enabled in Supabase), sign-in, the bearer token is attached to every API call, a case queue at `/cases`, and case detail at `/cases/:id` with status changes and risk history.

### Phase 3: LLM layer
- ✅ **3a. AI case brief**: `POST /cases/{id}/brief`. Gemini gets the scored features, SHAP drivers, the deterministic strategy tier and the risk-score history. It returns structured JSON: a summary, risk drivers, prioritized next actions and a compliant outreach draft.
  - The ML score and strategy tier stay authoritative. The LLM explains them and never overrides them.
  - PII minimization: borrower names are never sent to Gemini.
  - Prompt version, model, latency and token counts are stored with every brief for cost and quality tracking.
- ✅ `scripts/bench_gemini.py` measures 3.6 / 3.7 / 3.8 Flash latency with your key. Set `GEMINI_MODEL` to the winner.
- ✅ 3b. "AI case brief" card on the case page. The borrower's name is filled into the outreach draft in the browser, so it never reaches Gemini.

### Phase 4: Grounded RAG ⏳
- Ingest collection-policy docs (RBI Fair Practices Code, internal SOPs) into pgvector with Gemini embeddings.
- The brief cites the policy chunks it relied on. Replaces the hardcoded compliance rules in the prompt.

### Phase 5: Agentic workflow (human in the loop) ⏳
- Gemini function-calling agent with tools: `get_case_history`, `draft_outreach`, `schedule_follow_up`, `log_action`.
- Every side effect needs officer approval and is written to `audit_log`. The agent proposes, a human sends.

### Phase 5.5: Trustworthy risk logic ✅
- Signal audit, calibrated monotone model, RBI SMA/NPA policy floor, auto-named segments, retrain gate and behaviour tests. See `docs/MODEL_CARD.md`.

### Phase 6: MLOps and observability ⏳
- Log every prediction (already persisted from Phase 1). Nightly PSI drift job over feature distributions (GitHub Actions cron).
- Outcome capture: officers mark a case resolved or written off, which becomes labelled training data from real outcomes and replaces the 500 synthetic rows.
- Structured JSON logs and request IDs, plus Sentry free tier for errors.

### Phase 7: Frontend completion ⏳
- Re-score from the case page, and outreach approval (with Phase 5).

## Known limitation that no phase fixes by itself
The model is trained on 500 synthetic rows. Its reported metrics prove the
pipeline works, not that it's accurate on real borrowers. Phase 6 outcome
capture is the path to real data. Until then, present this as a demo.
