import pytest
from conftest import BORROWER, auth
from test_api import FakeLLM

from config.settings import settings
from main import app
from services.brief_service import get_llm_client


@pytest.fixture
def fake_llm():
    app.dependency_overrides[get_llm_client] = lambda: FakeLLM()
    yield
    app.dependency_overrides.clear()


def _case(client, user):
    r = client.post("/api/v1/predict", json=BORROWER, headers=auth(user))
    assert r.status_code == 200, r.text
    return r.json()["case_id"]


def test_anonymous_users_can_never_reach_the_llm(client, fake_llm):
    case_id = _case(client, "officer-1")
    assert client.post(f"/api/v1/cases/{case_id}/brief").status_code == 401


def test_default_limit_is_five_per_user_then_blocked(client, fake_llm):
    assert settings.brief_daily_limit_per_user == 5
    case_id = _case(client, "officer-1")
    for _ in range(5):
        assert client.post(f"/api/v1/cases/{case_id}/brief", headers=auth("officer-1")).status_code == 200
    blocked = client.post(f"/api/v1/cases/{case_id}/brief", headers=auth("officer-1"))
    assert blocked.status_code == 429

    me = client.get("/api/v1/me", headers=auth("officer-1")).json()
    assert me["briefs"]["used"] == 5 and me["briefs"]["limit"] == 5
    assert me["briefs"]["resets_at"] is not None


def test_global_cap_bounds_total_spend_across_accounts(client, fake_llm, monkeypatch):
    monkeypatch.setattr(settings, "brief_global_daily_limit", 2)
    for user in ("a", "b"):
        case_id = _case(client, user)
        assert client.post(f"/api/v1/cases/{case_id}/brief", headers=auth(user)).status_code == 200
    case_id = _case(client, "c")
    blocked = client.post(f"/api/v1/cases/{case_id}/brief", headers=auth("c"))
    assert blocked.status_code == 429
    assert "service-wide" in blocked.json()["detail"]


@pytest.mark.real_consent
def test_signed_in_user_must_accept_terms_before_using_the_app(client):
    headers = auth("new-user")
    me = client.get("/api/v1/me", headers=headers).json()
    assert me["consent_required"] is True

    blocked = client.post("/api/v1/predict", json=BORROWER, headers=headers)
    assert blocked.status_code == 403
    assert blocked.json()["detail"]["code"] == "consent_required"
    assert client.get("/api/v1/cases", headers=headers).status_code == 403

    stale = client.post("/api/v1/me/consent", json={"terms_version": "2000-01-01"}, headers=headers)
    assert stale.status_code == 409

    accepted = client.post("/api/v1/me/consent", json={"terms_version": me["terms_version"]}, headers=headers)
    assert accepted.json()["consent_required"] is False
    assert client.post("/api/v1/predict", json=BORROWER, headers=headers).json()["case_id"]


@pytest.mark.real_consent
def test_anonymous_predictor_needs_no_consent(client):
    assert client.post("/api/v1/predict", json=BORROWER).status_code == 200


@pytest.mark.real_consent
def test_new_terms_version_requires_fresh_consent(client, monkeypatch):
    headers = auth("returning-user")
    client.post("/api/v1/me/consent", json={"terms_version": settings.terms_version}, headers=headers)
    monkeypatch.setattr(settings, "terms_version", "2099-01-01")
    assert client.get("/api/v1/me", headers=headers).json()["consent_required"] is True
