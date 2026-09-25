import os
import sys
import time
from pathlib import Path

import jwt
import pytest

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

TEST_JWT_SECRET = "test-secret-at-least-32-bytes-long-000"
os.environ.setdefault("DATABASE_URL", f"sqlite:///{BACKEND / 'test.sqlite3'}")
os.environ["SUPABASE_JWT_SECRET"] = TEST_JWT_SECRET
os.environ["GEMINI_API_KEY"] = ""

from fastapi.testclient import TestClient  # noqa: E402

from db.models import Base  # noqa: E402
from db.session import get_engine  # noqa: E402
from main import app  # noqa: E402

BORROWER = {
    "first_name": "Asha",
    "last_name": "Verma",
    "gender": "Female",
    "age": 35,
    "monthly_income": 50000,
    "num_dependents": 2,
    "loan_type": "Personal",
    "loan_amount": 500000,
    "collateral_value": 100000,
    "outstanding_loan": 300000,
    "missed_payments": 3,
    "days_past_due": 90,
    "collection_attempts": 4,
}


def make_token(sub: str, role: str | None = None, secret: str = TEST_JWT_SECRET) -> str:
    claims = {"sub": sub, "aud": "authenticated", "exp": int(time.time()) + 600, "email": f"{sub}@example.com"}
    if role:
        claims["app_metadata"] = {"role": role}
    return jwt.encode(claims, secret, algorithm="HS256")


def auth(sub: str, role: str | None = None) -> dict:
    return {"Authorization": f"Bearer {make_token(sub, role)}"}


@pytest.fixture(scope="session", autouse=True)
def _schema():
    engine = get_engine()
    Base.metadata.create_all(engine)
    yield
    if engine.dialect.name == "sqlite":
        engine.dispose()
        Path(engine.url.database).unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def _clean_tables():
    yield
    with get_engine().begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
