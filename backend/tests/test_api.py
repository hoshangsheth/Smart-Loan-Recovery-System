import time
from types import SimpleNamespace

import jwt
from conftest import BORROWER, TEST_JWT_SECRET, auth, make_token
from sqlalchemy import func, select

from api.schemas.case import CaseBriefContent
from db.models import AuditLog, Case
from db.session import get_sessionmaker
from main import app
from services.brief_service import get_llm_client


def _count(model) -> int:
    with get_sessionmaker()() as db:
        return db.scalar(select(func.count()).select_from(model))


def _create_case(client, user="officer-1", **overrides) -> dict:
    r = client.post("/api/v1/predict", json={**BORROWER, **overrides}, headers=auth(user))
    assert r.status_code == 200, r.text
    return r.json()


def test_health_and_readiness(client):
    assert client.get("/health").json() == {"status": "ok"}
    ready = client.get("/health/ready").json()
    assert ready["status"] == "ok" and len(ready["model_version"]) == 12


def test_anonymous_predict_scores_but_persists_nothing(client):
    r = client.post("/api/v1/predict", json=BORROWER)
    assert r.status_code == 200
    body = r.json()
    assert body["case_id"] is None
    assert body["risk_category"] == "Critical Risk"
    assert 0.7 < body["risk_score"] < 0.9
    assert _count(Case) == 0


def test_invalid_token_is_rejected(client):
    bad = make_token("x", secret="wrong-secret-but-still-32-bytes-long!!")
    r = client.post("/api/v1/predict", json=BORROWER, headers={"Authorization": f"Bearer {bad}"})
    assert r.status_code == 401


def test_token_without_subject_is_rejected(client):
    token = jwt.encode({"aud": "authenticated", "exp": int(time.time()) + 60}, TEST_JWT_SECRET, algorithm="HS256")
    r = client.get("/api/v1/cases", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_cases_require_auth(client):
    assert client.get("/api/v1/cases").status_code == 401


def test_signed_in_predict_creates_case_with_audit(client):
    body = _create_case(client)
    assert body["case_id"]
    detail = client.get(f"/api/v1/cases/{body['case_id']}", headers=auth("officer-1")).json()
    assert detail["status"] == "open"
    assert len(detail["predictions"]) == 1
    assert detail["predictions"][0]["model_version"] == body["model_version"]
    assert _count(AuditLog) == 1


def test_officers_are_isolated_and_admin_sees_all(client):
    mine = _create_case(client, "officer-1")
    _create_case(client, "officer-2")

    assert len(client.get("/api/v1/cases", headers=auth("officer-1")).json()) == 1
    assert client.get(f"/api/v1/cases/{mine['case_id']}", headers=auth("officer-2")).status_code == 404
    assert len(client.get("/api/v1/cases", headers=auth("boss", role="admin")).json()) == 2


def test_queue_is_sorted_by_latest_risk(client):
    _create_case(client, collection_attempts=0, days_past_due=0, missed_payments=0)
    risky = _create_case(client)
    queue = client.get("/api/v1/cases", headers=auth("officer-1")).json()
    assert queue[0]["id"] == risky["case_id"]
    assert queue[0]["latest_risk_score"] >= queue[1]["latest_risk_score"]


def test_rescore_appends_history_and_keeps_borrower_ref(client):
    first = _create_case(client)
    r = client.post(
        f"/api/v1/cases/{first['case_id']}/predictions",
        json={**BORROWER, "days_past_due": 150, "collection_attempts": 7},
        headers=auth("officer-1"),
    )
    assert r.status_code == 200
    assert r.json()["borrower_id"] == first["borrower_id"]
    detail = client.get(f"/api/v1/cases/{first['case_id']}", headers=auth("officer-1")).json()
    assert len(detail["predictions"]) == 2


def test_status_update(client):
    case_id = _create_case(client)["case_id"]
    r = client.patch(f"/api/v1/cases/{case_id}", json={"status": "in_progress"}, headers=auth("officer-1"))
    assert r.json()["status"] == "in_progress"
    assert client.get("/api/v1/cases?status=open", headers=auth("officer-1")).json() == []


def test_brief_unconfigured_returns_503(client):
    case_id = _create_case(client)["case_id"]
    assert client.post(f"/api/v1/cases/{case_id}/brief", headers=auth("officer-1")).status_code == 503


class FakeLLM:
    def __init__(self):
        self.calls = []
        self.models = self

    def generate_content(self, *, model, contents, config):
        self.calls.append({"model": model, "contents": contents, "config": config})
        return SimpleNamespace(
            parsed=CaseBriefContent(
                summary="Borrower is 90 days past due with 4 collection attempts.",
                key_risk_drivers=["Collection attempts = 4 increased risk"],
                recommended_actions=[
                    {"action": "Call borrower", "rationale": "DPD 90", "priority": "immediate", "channel": "call"}
                ],
                outreach_draft="Dear {borrower_name}, please contact us to discuss a payment plan.",
                caveats=[],
            ),
            usage_metadata=SimpleNamespace(prompt_token_count=900, candidates_token_count=250),
        )


def test_brief_generation_persists_and_keeps_pii_out_of_prompt(client):
    fake = FakeLLM()
    app.dependency_overrides[get_llm_client] = lambda: fake
    try:
        case_id = _create_case(client)["case_id"]
        r = client.post(f"/api/v1/cases/{case_id}/brief", headers=auth("officer-1"))
    finally:
        app.dependency_overrides.clear()

    assert r.status_code == 200, r.text
    brief = r.json()
    assert brief["prompt_version"] == "brief-v1"
    assert brief["input_tokens"] == 900
    assert brief["content"]["recommended_actions"][0]["channel"] == "call"

    prompt = fake.calls[0]["contents"]
    assert "Asha" not in prompt and "Verma" not in prompt and "Female" not in prompt
    assert '"risk_score"' in prompt and '"strategy_tier"' in prompt

    detail = client.get(f"/api/v1/cases/{case_id}", headers=auth("officer-1")).json()
    assert detail["latest_brief"]["id"] == brief["id"]


def test_brief_daily_quota_applies_to_officers_not_admins(client, monkeypatch):
    from config.settings import settings

    monkeypatch.setattr(settings, "brief_daily_limit_per_user", 1)
    app.dependency_overrides[get_llm_client] = lambda: FakeLLM()
    try:
        case_id = _create_case(client)["case_id"]
        assert client.post(f"/api/v1/cases/{case_id}/brief", headers=auth("officer-1")).status_code == 200
        blocked = client.post(f"/api/v1/cases/{case_id}/brief", headers=auth("officer-1"))
        assert blocked.status_code == 429
        assert "limit" in blocked.json()["detail"]
        admin = auth("boss", role="admin")
        assert client.post(f"/api/v1/cases/{case_id}/brief", headers=admin).status_code == 200
        assert client.post(f"/api/v1/cases/{case_id}/brief", headers=admin).status_code == 200
    finally:
        app.dependency_overrides.clear()
