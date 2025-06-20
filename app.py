import streamlit as st
import pickle
import numpy as np
import pandas as pd

# Load the trained model
with open("PKL Files/xgb.pkl", "rb") as file:
    model = pickle.load(file)

# Recovery strategy function
def assign_recovery_strategy(risk_score):
    if risk_score > 0.75:
        return ("Initiate legal proceedings with asset seizure notices, "
                "escalate to external recovery agencies, and enforce loan recovery under default clauses.")
    elif 0.50 <= risk_score <= 0.75:
        return ("Offer structured settlements with penal interest adjustments, "
                "negotiate revised EMI plans, and initiate soft legal notices.")
    else:
        return ("Send automated payment reminders, schedule regular financial health reviews, "
                "and maintain active borrower engagement for early warnings.")

# Streamlit UI
st.set_page_config(page_title="Smart Loan Recovery System", layout="centered")
st.title("🔍 Smart Loan Recovery System")
st.markdown("### 📋 Enter Borrower Details Below")

# User Inputs
age = st.number_input("Age", min_value=18, max_value=100, step=1)
monthly_income = st.number_input("Monthly Income (₹)", min_value=0)
num_dependents = st.number_input("Number of Dependents", min_value=0, step=1)
loan_amount = st.number_input("Loan Amount (₹)", min_value=10000)
loan_tenure = st.number_input("Loan Tenure (in Months)", min_value=6, max_value=360, step=1)
interest_rate = st.number_input("Interest Rate (%)", min_value=1.0, max_value=40.0, step=0.1)
collateral_value = st.number_input("Collateral Value (₹)", min_value=0)
outstanding_loan = st.number_input("Outstanding Loan Amount (₹)", min_value=0)
monthly_emi = st.number_input("Monthly EMI (₹)", min_value=0)
missed_payments = st.number_input("Number of Missed Payments", min_value=0, step=1)
days_past_due = st.number_input("Days Past Due", min_value=0)

# Auto-calculated fields
emi_to_income = round(monthly_emi / monthly_income, 3) if monthly_income else 0.0
collateral_coverage = round(collateral_value / loan_amount, 3) if loan_amount else 0.0
default_severity = missed_payments * days_past_due

if st.button("🔐 Predict Risk & Recommend Strategy"):
    # Feature input list
    features = np.array([[age, monthly_income, num_dependents, loan_amount, loan_tenure,
                          interest_rate, collateral_value, outstanding_loan, monthly_emi,
                          missed_payments, days_past_due, emi_to_income,
                          collateral_coverage, default_severity]])

    # Predict risk
    risk_score = model.predict_proba(features)[0][1]
    strategy = assign_recovery_strategy(risk_score)

    # Output
    st.markdown("### 🧠 Predicted Risk Score:")
    st.success(f"{risk_score:.2%}")

    st.markdown("### 🎯 Recommended Recovery Strategy:")
    st.info(strategy)