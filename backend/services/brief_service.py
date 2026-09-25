"""
AI case brief generation with Gemini.

The XGBoost score and the rule-based strategy tier stay authoritative. The
LLM explains them and turns them into next actions; it never produces or
changes a score. The prompt only carries numeric and enum fields (no names,
no free text), which keeps borrower PII out of the LLM provider and leaves
no user-controlled text to inject instructions through.
"""
import json
import time
from functools import lru_cache

from fastapi import HTTPException, status
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from api.schemas.case import CaseBriefContent
from config.settings import settings
from db.models import Case, CaseBrief, Prediction

PROMPT_VERSION = "brief-v1"
MAX_HISTORY = 10

SYSTEM_INSTRUCTION = """You are a senior loan-recovery analyst at an Indian lender, briefing a recovery officer on one borrower case.

Rules:
- The risk score, risk category and strategy tier in the case data come from a validated ML model and policy engine. Treat them as given. Never restate a different score or tier, and never recommend actions harsher than the strategy tier allows.
- Ground every claim in the case data. Cite the actual numbers. If the data can't support something, say so in caveats rather than guessing.
- Top risk drivers are SHAP attributions: "increased" means that feature pushed risk up for this borrower.
- If risk_history has several entries, comment on the trend.
- Follow the RBI Fair Practices Code for recovery: no threats, intimidation, public shaming or contact with third parties about the debt; contact only between 8 AM and 7 PM; respectful language; always offer a way to discuss restructuring or a payment plan before escalation.
- Legal notices are appropriate only when the strategy tier already calls for legal action.
- The outreach draft goes to the borrower. Keep it under 90 words, use {borrower_name} as the only name, and don't mention the risk score or internal categories."""


def build_case_context(case: Case, predictions: list[Prediction]) -> dict:
    latest = predictions[-1]
    inp = latest.input
    return {
        "loan_type": case.loan_type,
        "case_status": case.status,
        "model_output": {
            "risk_score": round(latest.risk_score, 4),
            "risk_category": latest.risk_category,
            "strategy_tier": latest.strategy,
            "borrower_segment": latest.segment.get("segment_name"),
        },
        "borrower_financials": {
            "age": inp["age"],
            "num_dependents": inp["num_dependents"],
            "monthly_income_inr": inp["monthly_income"],
            "loan_amount_inr": inp["loan_amount"],
            "outstanding_loan_inr": inp["outstanding_loan"],
            "collateral_value_inr": inp["collateral_value"],
            "missed_payments": inp["missed_payments"],
            **latest.calculated,
        },
        "top_risk_drivers": [
            {"feature": f["feature"], "value": f["value"], "effect": f["direction"]}
            for f in latest.shap_top_features
        ],
        "risk_history": [
            {
                "scored_at": p.created_at.date().isoformat(),
                "risk_score": round(p.risk_score, 4),
                "days_past_due": p.calculated["days_past_due"],
                "collection_attempts": p.calculated["collection_attempts"],
            }
            for p in predictions[-MAX_HISTORY:]
        ],
    }


@lru_cache
def get_llm_client() -> genai.Client:
    if not settings.gemini_api_key:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "AI briefs are not configured (GEMINI_API_KEY unset)")
    return genai.Client(
        api_key=settings.gemini_api_key,
        http_options=types.HttpOptions(
            timeout=settings.gemini_timeout_ms,
            retry_options=types.HttpRetryOptions(attempts=3, http_status_codes=[429, 500, 503]),
        ),
    )


def generate_brief(client: genai.Client, case: Case, predictions: list[Prediction], user_id: str) -> CaseBrief:
    context = build_case_context(case, predictions)
    started = time.perf_counter()
    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=f"Case data (JSON):\n{json.dumps(context, indent=2, default=str)}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=CaseBriefContent,
                temperature=0.2,
                thinking_config=types.ThinkingConfig(thinking_level=settings.gemini_thinking_level),
            ),
        )
    except genai_errors.APIError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"LLM provider error: {exc.message}") from exc
    latency_ms = int((time.perf_counter() - started) * 1000)

    content = response.parsed
    if not isinstance(content, CaseBriefContent):
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "LLM returned an unusable brief")

    usage = response.usage_metadata
    return CaseBrief(
        case_id=case.id,
        prediction_id=predictions[-1].id,
        created_by=user_id,
        llm_model=settings.gemini_model,
        prompt_version=PROMPT_VERSION,
        content=content.model_dump(mode="json"),
        latency_ms=latency_ms,
        input_tokens=usage.prompt_token_count if usage else None,
        output_tokens=usage.candidates_token_count if usage else None,
    )
