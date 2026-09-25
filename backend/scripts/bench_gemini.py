"""
Benchmark Gemini Flash models on the real case-brief prompt.

    GEMINI_API_KEY=... python scripts/bench_gemini.py --runs 5

Reports latency p50/p95, token usage, cost per brief, and schema-valid rate
so GEMINI_MODEL is chosen on measured numbers, not marketing.
"""
import argparse
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.schemas.borrower import BorrowerInput  # noqa: E402
from config.settings import settings  # noqa: E402
from db.models import Case, Prediction  # noqa: E402
from models.loader import get_ml_artifacts  # noqa: E402
from services import brief_service  # noqa: E402
from services.scoring_service import score_borrower  # noqa: E402

DEFAULT_MODELS = ["gemini-3.6-flash", "gemini-3.7-flash", "gemini-3.8-flash"]
# USD per 1M tokens (input, output). Promo pricing valid until 2026-12-31; update after.
PRICING = {m: (0.75, 3.75) for m in DEFAULT_MODELS}

SAMPLE = BorrowerInput(
    first_name="Sample", last_name="Borrower", gender="Male", age=41, monthly_income=62000, num_dependents=3,
    loan_type="Business", loan_amount=900000, collateral_value=250000, outstanding_loan=610000,
    missed_payments=4, days_past_due=120, collection_attempts=6,
)


def _sample_case() -> tuple[Case, list[Prediction]]:
    result = score_borrower(SAMPLE, get_ml_artifacts())
    case = Case(id="bench", loan_type=SAMPLE.loan_type.value, status="open")
    prediction = Prediction(
        id="bench-pred",
        risk_score=result.risk_score,
        risk_category=result.risk_category,
        strategy=result.strategy,
        input=result.input.model_dump(mode="json"),
        calculated=result.calculated.model_dump(mode="json"),
        segment=result.segment.model_dump(mode="json"),
        shap_top_features=[f.model_dump(mode="json") for f in result.shap_top_features],
        created_at=datetime.now(UTC),
    )
    return case, [prediction]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    parser.add_argument("--runs", type=int, default=5)
    args = parser.parse_args()

    client = brief_service.get_llm_client()
    case, predictions = _sample_case()

    print(f"{'model':<22}{'p50 ms':>9}{'p95 ms':>9}{'in tok':>8}{'out tok':>8}{'$/1k briefs':>13}{'ok':>6}")
    for model in args.models:
        settings.gemini_model = model
        latencies, tin, tout, ok = [], [], [], 0
        for _ in range(args.runs):
            try:
                brief = brief_service.generate_brief(client, case, predictions, "bench")
            except Exception as exc:  # noqa: BLE001
                print(f"  {model}: {getattr(exc, 'detail', exc)}")
                continue
            ok += 1
            latencies.append(brief.latency_ms)
            tin.append(brief.input_tokens or 0)
            tout.append(brief.output_tokens or 0)
        if not latencies:
            continue
        p95 = sorted(latencies)[max(0, int(len(latencies) * 0.95) - 1)]
        price_in, price_out = PRICING.get(model, (0.0, 0.0))
        cost = (statistics.mean(tin) * price_in + statistics.mean(tout) * price_out) / 1e6 * 1000
        print(
            f"{model:<22}{statistics.median(latencies):>9.0f}{p95:>9.0f}"
            f"{statistics.mean(tin):>8.0f}{statistics.mean(tout):>8.0f}{cost:>13.2f}{ok:>4}/{args.runs}"
        )


if __name__ == "__main__":
    main()
