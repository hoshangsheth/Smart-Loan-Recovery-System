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

Install dependencies.

```bash
pip install -r backend/requirements.txt
```

Start the FastAPI server.

```bash
uvicorn backend.main:app --reload
```

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

| Method | Endpoint   | Description                   |
| ------ | ---------- | ----------------------------- |
| GET    | `/`        | Health Check                  |
| POST   | `/predict` | Predict borrower default risk |
| GET    | `/health`  | API Status                    |

> Actual endpoints may differ depending on the current implementation.

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

# Future Enhancements

* Borrower segmentation
* Explainable AI (SHAP)
* LLM-powered recovery assistant
* Portfolio risk monitoring
* Model retraining pipeline
* Authentication & user management
* Audit logs
* Automated recovery workflows
* Notification system
* Cloud model storage

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
