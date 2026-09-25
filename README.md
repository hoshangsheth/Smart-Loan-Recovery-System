# Recovia - ML-Powered Smart Loan Recovery System

Recovia is an AI-powered decision support platform designed to help financial institutions identify high-risk borrowers, predict loan defaults, and recommend appropriate recovery strategies. By combining machine learning with an intuitive dashboard, Recovia enables lenders to make faster, data-driven recovery decisions while reducing financial risk.

> **Status:** MVP (Minimum Viable Product)

---

# Overview

Loan defaults are a significant challenge for banks and lending institutions. Traditional recovery methods often rely on manual analysis and fixed rules, making them slow, inconsistent, and difficult to scale.

Recovia leverages machine learning to automate borrower risk assessment and provide actionable insights for recovery teams.

The platform analyzes borrower information, predicts the likelihood of default, estimates repayment risk, and assists recovery officers in prioritizing accounts requiring immediate attention.

---

# Key Features

* ML-powered loan default prediction
* Borrower risk assessment
* Intelligent recovery recommendations
* Credit risk visualization dashboard
* Interactive analytics
* FastAPI REST API
* Modern React frontend
* Modular backend architecture
* Production-ready project structure

---

# Tech Stack

## Frontend

* React
* Vite
* JavaScript
* CSS
* Axios

## Backend

* FastAPI
* Python
* Uvicorn
* Pydantic

## Data, Auth & AI

* Supabase Postgres (SQLAlchemy, Alembic) and Supabase Auth
* Google Gemini Flash (structured-output case briefs)

## Machine Learning

* Scikit-learn
* XGBoost
* Pandas
* NumPy
* Joblib

---

# Project Structure

```text
Recovia/
│
├── backend/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── services/
│   ├── utils/
│   ├── ml_artifacts/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

---

# Machine Learning Pipeline

The prediction pipeline follows these stages:

```text
Borrower Information
        │
        ▼
Feature Engineering
        │
        ▼
Data Preprocessing
        │
        ▼
Risk Prediction Model
        │
        ▼
Risk Score
        │
        ▼
Recovery Recommendation
```

---

# Input Features

The model evaluates various borrower characteristics, including:

* Age
* Annual Income
* Employment Status
* Loan Amount
* Interest Rate
* Loan Tenure
* Credit Score
* Existing Debt
* EMI-to-Income Ratio
* Collateral Value
* Previous Defaults
* Payment History
* Loan Purpose

> The exact features depend on the trained model included in the project.

---

# Installation

## Clone the repository

```bash
git clone https://github.com/hoshangsheth/recovia.git

cd recovia
```

---

## Backend Setup

Create a virtual environment.

```bash
python -m venv venv
```

Activate it.

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies, apply migrations, and start the server (run from `backend/`).

```bash
cd backend
pip install -r requirements-dev.txt
cp .env.example .env            # fill in DATABASE_URL, SUPABASE_URL, GEMINI_API_KEY
alembic upgrade head            # SQLite by default; Supabase Postgres when DATABASE_URL is set
uvicorn main:app --reload
```

Run the checks CI runs:

```bash
ruff check . && pytest -q
```

### Supabase setup (free tier)

1. Create a project. Copy the **Session pooler** connection string into `DATABASE_URL`, changing the scheme to `postgresql+psycopg://`.
2. Set `SUPABASE_URL=https://<ref>.supabase.co`. Tokens are verified against the project's JWKS. Only legacy HS256 projects need `SUPABASE_JWT_SECRET`.
3. To make someone an admin (sees every case), set `{"role": "admin"}` in their `app_metadata`.
4. Set the `BACKEND_URL` repository variable on GitHub so the daily keepalive workflow stops the free project from pausing.

### Choosing the Gemini model

```bash
GEMINI_API_KEY=... python scripts/bench_gemini.py --runs 5
```

Put the fastest model that returns valid output on every run into `GEMINI_MODEL`.

API Documentation

```
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

Navigate into the frontend directory.

```bash
cd frontend
```

Install dependencies.

```bash
npm install
```

Run the application.

```bash
npm run dev
```

Open:

```
http://localhost:5173
```

---

# API

Example endpoints include:

| Method | Endpoint | Auth | Description |
| ------ | -------- | ---- | ----------- |
| GET | `/health` | - | Liveness |
| GET | `/health/ready` | - | Readiness (checks DB, returns model version) |
| POST | `/api/v1/predict` | optional | Score a borrower. When signed in, also saves a case |
| GET | `/api/v1/cases` | required | Case queue, highest current risk first (`?status=open`) |
| GET | `/api/v1/cases/{id}` | required | Case detail with full scoring history and latest AI brief |
| POST | `/api/v1/cases/{id}/predictions` | required | Re-score with updated DPD/collections data |
| PATCH | `/api/v1/cases/{id}` | required | Change case status |
| POST | `/api/v1/cases/{id}/brief` | required | Generate a Gemini case brief (summary, drivers, actions, outreach draft) |
| POST | `/api/v1/analytics`, `/api/v1/report` | - | Dashboard data and PDF report |

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the phased plan.

---

# Dashboard Capabilities

The dashboard provides insights such as:

* Borrower profile
* Default probability
* Loan risk level
* Feature importance
* Risk distribution
* Portfolio analytics
* Recovery recommendations

---

# Model Artifacts

The project includes pre-trained machine learning artifacts required for inference, such as:

* Trained prediction model
* Feature metadata
* Encoders
* Preprocessing objects

These files are stored under:

```text
backend/ml_artifacts/
```

---

# Deployment

Frontend

* Vercel

Backend

* Render
* Docker

---

# Model Performance

The XGBoost classifier is trained against actual observed loan outcomes
(`Recovery_Status`: Fully Recovered vs. Partially Recovered/Written Off),
not a proxy label. Evaluated on a held-out test set (150 borrowers, never
seen during training):

| Metric | Score |
|---|---|
| Accuracy | 86% |
| Precision (at-risk class) | 93% |
| Recall (at-risk class) | 70% |
| F1 | 80% |
| ROC-AUC | 0.83 |

Reproducible via `backend/retrain.py`.

---

# Future Enhancements

* Explainable AI (SHAP)
* LLM-powered recovery assistant
* Portfolio risk monitoring
* Authentication & user management
* Audit logs
* Automated recovery workflows
* Notification system
* Cloud model storage
* Larger training dataset (current: 500 synthetic borrower records — expand for production-grade reliability)

---

# Engineering Principles

Recovia is built following modern software engineering practices:

* Single Responsibility Principle (SRP)
* Modular architecture
* Separation of concerns
* API-first design
* Scalable backend structure
* Production-oriented development
* Incremental MVP approach

---

# Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push your branch.
5. Open a Pull Request.

---

# License

This project is licensed under the MIT License.

---

# Author

**Hoshang Sheth**

GenAI & AI Engineer

Portfolio: https://hoshangsheth.com

GitHub: https://github.com/hoshangsheth

LinkedIn: https://linkedin.com/in/hoshangsheth
