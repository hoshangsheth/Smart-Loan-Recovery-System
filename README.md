# Smart Loan Recovery System

A Machine Learning-powered solution to optimize loan recovery strategies by predicting the most effective collection method for each borrower — reducing defaults, legal costs, and manual effort.

---

## Project Overview

Loan recovery is often inefficient due to generic collection approaches. This project automates and personalizes recovery decisions using borrower data, machine learning, and risk segmentation.

The system:
- Identifies high-risk borrowers early
- Suggests recovery strategies (legal, follow-up, settlement, etc.)
- Provides actionable insights via an interactive dashboard

---

## Core Features

- **Risk Prediction**: XGBoost model to classify borrowers based on default likelihood.
- **Feature Engineering**: Includes EMI-to-Income Ratio, Collateral Coverage, Default Severity, and more.
- **Clustering & Segmentation**: Groups borrowers based on financial profiles and risk.
- **Legal Action Integration**: Suggests when legal steps should be taken based on risk score and history.
- **Streamlit App**: UI for lenders to input borrower details, get predictions, and view portfolio insights.

---

## Tech Stack

- **Python**, **Pandas**, **NumPy**, **Matplotlib**, **Seaborn**
- **XGBoost**, **Random Forest**, **KMeans**
- **Streamlit** for app deployment
- **Scikit-learn** for preprocessing and modeling
- **Joblib** for model serialization

---

## Impact

- Automated decision-making reduced manual effort in identifying suitable recovery strategies.
- Early risk detection helped flag high-risk borrowers and reduce defaults.
- Cost optimization by recommending legal action only when necessary.
- Data-driven recovery provided real-time, explainable insights through an interactive dashboard.
- Improved loan portfolio health and enhanced recovery rates for financial institutions.

## Future Enhancements

- Early warning system to notify lenders of potential defaults before they occur.
- Automated borrower communication through SMS/email reminders for missed payments.
- Cost-sensitive learning to balance recovery strategies with operational expenses.
- Reinforcement learning to dynamically adapt and optimize recovery policies.
- REST API integration for scalable use within larger fintech platforms.

---

## Getting Started – Clone & Run Locally

Follow these steps to clone the project and run it on your local machine:

### 1. Clone the Repository

```bash
git clone https://github.com/hoshangsheth/smart-loan-recovery-system.git
cd smart-loan-recovery-system
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate      # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit App
```bash
streamlit run app.py
```
---
