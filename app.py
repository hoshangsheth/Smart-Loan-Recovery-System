import streamlit as st
import pickle
import numpy as np

# Load model
try:
    with open("PKL Files/xgb.pkl", "rb") as file:
        model = pickle.load(file)
except Exception as e:
    st.error("❌ Failed to load the model. Please check the path or file integrity.")
    st.stop()

# Load features
try:
    with open("PKL Files/features.pkl", "rb") as f:
        features_list = pickle.load(f)
except Exception as e:
    st.error("❌ Feature list could not be loaded.")
    st.stop()

# Recovery strategy logic
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

# EMI Calculation
def calculate_emi(P, annual_rate, n):
    try:
        if P <= 0 or annual_rate <= 0 or n <= 0:
            return 0
        r = annual_rate / (12 * 100)
        emi = (P * r * (1 + r)**n) / ((1 + r)**n - 1)
        return round(emi, 2)
    except Exception:
        return 0

# Page layout
st.set_page_config(page_title="Smart Loan Recovery System", layout="centered")
st.title("🔍 Smart Loan Recovery System")
st.markdown("### 📋 Enter Borrower Details Below")

# Borrower Inputs
col1, col2 = st.columns(2)
with col1:
    first_name = st.text_input("First Name")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
with col2:
    last_name = st.text_input("Last Name")
    loan_amount = st.number_input("Loan Amount (₹)", min_value=10000)

# Numerical fields
age = st.number_input("Age", min_value=18, max_value=100)
monthly_income = st.number_input("Monthly Income (₹)", min_value=0)
num_dependents = st.number_input("Number of Dependents", min_value=0, step=1)
loan_tenure = st.number_input("Loan Tenure (Months)", min_value=6, max_value=360)
interest_rate = st.number_input("Interest Rate (%)", min_value=1.0, max_value=40.0)
outstanding_loan = st.number_input("Outstanding Loan Amount (₹)", min_value=0)
collection_attempts = st.number_input("Collection Attempts", min_value=0, max_value=10)
missed_payments = st.number_input("Missed Payments", min_value=0)
days_past_due = st.number_input("Days Past Due", min_value=0)
collateral_value = st.number_input("Collateral Value (₹)", min_value=0)

# EMI
monthly_emi = calculate_emi(loan_amount, interest_rate, loan_tenure)
if monthly_emi == 0:
    st.warning("⚠️ EMI not calculated. Ensure loan amount, interest rate, and tenure are all greater than 0.")
else:
    st.markdown(f"**Calculated Monthly EMI**: ₹{monthly_emi:,.2f}")

# Engineered features
try:
    emi_to_income = round(monthly_emi / monthly_income, 3) if monthly_income else 0
except ZeroDivisionError:
    emi_to_income = 0.0

collateral_coverage = round(collateral_value / loan_amount, 3) if loan_amount else 0
default_severity = missed_payments * days_past_due

# Predict button
if st.button("🔐 Predict Risk & Recommend Strategy"):
    if not first_name or not last_name:
        st.error("❌ Please enter the borrower's full name.")
    elif monthly_income == 0:
        st.error("❌ Monthly income must be greater than 0 to calculate EMI-to-Income ratio.")
    elif loan_amount == 0 or loan_tenure == 0 or interest_rate == 0:
        st.error("❌ Fill in all loan details to proceed.")
    else:
        try:
            input_features = np.array([[age, monthly_income, num_dependents, loan_tenure, interest_rate,
                                        outstanding_loan, collection_attempts,
                                        emi_to_income, collateral_coverage, default_severity]])
            
            risk_score = model.predict_proba(input_features)[0][1]
            strategy = assign_recovery_strategy(risk_score)

            # Display results
            st.markdown("---")
            st.subheader("📌 Borrower Summary")
            st.markdown(f"**Name**: {first_name} {last_name}  \n"
                        f"**Gender**: {gender}  \n"
                        f"**Loan Amount**: ₹{loan_amount:,.0f}  \n"
                        f"**EMI**: ₹{monthly_emi:,.0f}  \n"
                        f"**Outstanding Loan**: ₹{outstanding_loan:,.0f}")

            st.subheader("🧠 Predicted Risk Score:")
            st.success(f"{risk_score:.2%}")

            st.subheader("🎯 Recommended Recovery Strategy:")
            st.info(strategy)
        except Exception as e:
            st.error("❌ Prediction failed. Please check input values or model integrity.")
            st.exception(e)