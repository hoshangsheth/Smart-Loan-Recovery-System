import time
import random
import string

# Generate unique borrower ID for PDF
def generate_borrower_id(loan_type, first_name, last_name):
    loan_code = loan_type[:3].upper() if loan_type else 'GEN'
    initials = (first_name[0].upper() if first_name else 'X') + (last_name[0].upper() if last_name else 'X')
    timestamp = str(int(time.time()))
    random_hex = ''.join(random.choices(string.hexdigits.upper(), k=4))
    return f"{loan_code}-{initials}-{timestamp}-{random_hex}"
import streamlit as st
# Import required modules
import math
from streamlit_option_menu import option_menu
import pickle
import numpy as np
import plotly.express as px
import pandas as pd
# For PDF generation
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# -------------------------------
# Load Model and Features
# -------------------------------
with open("PKL Files/xgb_tuned.pkl", "rb") as f:
    model = pickle.load(f)

with open("PKL Files/features.pkl", "rb") as f:
    features_list = pickle.load(f)

# -------------------------------
# Utility Functions
# Function to map loan types to default interest and tenure
def get_default_loan_terms(loan_type):
    loan_type = loan_type.lower()
    mapping = {
        "personal": (14.0, 48),
        "auto": (10.5, 60),
        "business": (16.0, 36),
        "home": (9.0, 180)
    }
    return mapping.get(loan_type, (15.0, 36))  # Fallback
# -------------------------------
# def assign_recovery_strategy(score):
#     if score > 0.85:
#         return ("Initiate legal proceedings with asset seizure notices, "
#                 "escalate to external recovery agencies, and enforce loan recovery under default clauses."), "Very High Risk"
#     elif 0.35 <= score <= 0.85:
#         return ("Offer structured settlements with penal interest adjustments, "
#                 "negotiate revised EMI plans, and initiate soft legal notices."), "Medium Risk"
#     else:
#         return ("Send automated payment reminders, schedule regular financial health reviews, "
#                 "and maintain active borrower engagement for early warnings."), "Low Risk"

def assign_recovery_strategy(score, dpd):
    if score > 0.90:
        if dpd >= 90:
            return (
                "Initiate legal proceedings, send final demand notices with collateral seizure intent, "
                "escalate case to external recovery agencies, and flag borrower as a chronic defaulter.",
                "🚨 Critical Risk"
            )
        else:
            return (
                "Send pre-litigation warning, offer limited time restructuring, and escalate to senior recovery team.",
                "🚩 High Risk"
            )

    elif 0.75 < score <= 0.90:
        return (
            "Offer one-time settlement options or revised repayment terms, "
            "escalate to senior collections team, and issue a pre-litigation warning.",
            "🚩 High Risk"
        )

    elif 0.25 < score <= 0.75:
        return (
            "Trigger multiple soft recovery attempts including calls, emails, and WhatsApp nudges. "
            "Offer flexible EMI restructuring plans and conduct borrower behavior analysis.",
            "⚠️ Medium Risk"
        )

    else:
        return (
            "Send timely automated reminders via SMS/email, monitor payment behavior closely, "
            "and provide financial advisory nudges to maintain repayment consistency.",
            "✔️ Low Risk"
        )

def calculate_emi(P, annual_rate, n):
    if P in (None, 0) or annual_rate in (None, 0) or n in (None, 0):
        return None
    r = annual_rate / (12 * 100)
    emi = (P * r * (1 + r)**n) / ((1 + r)**n - 1)
    return round(emi, 2)

# -------------------------------
# Streamlit Multi-Page Simulation
# -------------------------------
# ---------- Custom CSS ----------
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #0F0F1C;
            padding-top: 20px;
        }
        .menu-container {
            background: linear-gradient(135deg, #00F260, #0575E6);
            padding: 15px;
            border-radius: 10px;
        }
        .stButton>button {
            border-radius: 8px;
            background-color: #8A2BE2;
            color: white;
            padding: 10px 24px;
            transition: 0.3s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #BA55D3;
            transform: scale(1.05);
        }
        h1, h2, h3 {
            color: white;
        }
        .header-container {
            background: #12122b;
            border-radius: 15px;
            padding: 10px 15px;
            text-align: left;
            color: white;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 12px;
            border: 2px solid #2f2f4f;
        }
        .header-container img {
            width: 50px;
            height: 50px;
        }
        .icon-text {
            font-size: 18px;
        }
        .css-1v0mbdj.ef3psqc12 {
            padding: 0px;
        }
        /* Option menu tweaks for dark sidebar */
        .css-1d391kg, .css-1d391kg .nav-link {
            background: transparent !important;
            color: #fff !important;
            border-radius: 10px !important;
            margin-bottom: 8px !important;
            font-weight: 600 !important;
            font-size: 1.08em !important;
            transition: background 0.2s;
        }
        .css-1d391kg .nav-link.active {
            background: #0575E6 !important;
            color: #fff !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 8px rgba(5,117,230,0.08);
        }
    </style>
""", unsafe_allow_html=True)


with st.sidebar:
    # Sidebar header with icon and app name
    st.markdown(f"""
        <div class="header-container">
            <img src="https://cdn-icons-png.flaticon.com/512/3427/3427890.png" />
            <span class="icon-text">Smart Loan<br>Recovery System</span>
        </div>
    """, unsafe_allow_html=True)

    page = option_menu(
        menu_title="Main Menu",
        options=["Overview", "Smart Risk Predictor", "Recovery Insights","Contact Us"],
        icons=["house", "currency-dollar", "graph-up","envelope"],
        menu_icon="bank",
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "#0F0F1C"},
            "icon": {"color": "#0ABAB5", "font-size": "20px"},
            "nav-link": {
                "color": "white",
                "font-size": "16px",
                "text-align": "left",
                "margin": "2px",
                "--hover-color": "#0B1D51"
            },
            "nav-link-selected": {
                "background-color": "#FFFBDE",
                "color": "black",
                "font-weight": "bold"
            },
        }
    )

    st.markdown(
    """
    <hr style="border-color: #4B0082; margin-top: 20px; margin-bottom: 5px;">
    <p style="text-align: center; color: #ccc; font-size: 14px; margin-bottom: 8px;">
        Connect with me here
    </p>
    <div style="display: flex; justify-content: center; gap: 20px; padding-bottom: 10px;">
        <a href="https://www.linkedin.com/in/hoshangsheth" target="_blank" style="text-decoration: none;">
            <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="LinkedIn" width="28">
        </a>
        <a href="https://github.com/hoshangsheth" target="_blank" style="text-decoration: none;">
            <img src="https://cdn-icons-png.flaticon.com/512/733/733553.png" alt="GitHub" width="28">
        </a>
        <a href="https://hoshangsheth.carrd.co/#" target="_blank" style="text-decoration: none;">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" alt="Portfolio" width="28">
        </a>
    </div>
    """,
    unsafe_allow_html=True
    )

# -------------------------------
# HOME PAGE
# -------------------------------

if page == "Overview":
    # Add a finance/loan themed background image for Home page only, dimmed by 50%
    st.markdown(
        """
        <style>
        .stApp {
            position: relative;
            background-image: url('https://images.unsplash.com/photo-1501167786227-4cba60f6d58f?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        .stApp::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(11, 29, 81, 0.5); /* #0B1D51 at 50% opacity */
            z-index: 0;
        }
        .stApp > * {
            position: relative;
            z-index: 1;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <h1 style="
            font-size: 4.2em;
            color: #FFFBDE;
            font-weight: bold;
            text-align: center;
        ">
            🏛️ Smart Loan Recovery System
        </h1>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        st.markdown("""
        <div style="
            background: #0B1D51;
            border: 2px solid #6a0dad;
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            color: #FFFBDE;
            font-size: 1.08rem;
            line-height: 1.8;
            box-shadow: 0 0 10px rgba(106, 13, 173, 0.3);
        ">
        This intelligent platform predicts the <b>risk of borrower default</b> and suggests <b>optimal recovery strategies</b> for financial institutions.<br><br>
        <b>✔ Powered by XGBoost</b> with behavioral, financial, and engineered features.<br>
        <b>✔ Segment-based recommendations</b> for early intervention.<br>
        <b>✔ Visualizes borrower patterns</b> for actionable business insights.<br>
        <b>✔ Modern, interactive dashboard</b> for risk managers and recovery teams.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h4 style='color:#FFFBDE; margin-top:30px;'>🔍︎ Predict Borrower Risk Instantly</h4>", unsafe_allow_html=True)
        st.markdown("""
        <div style="
            background: #0B1D51;
            border: 2px solid #6a0dad;
            border-radius: 15px;
            padding: 15px;
            margin-top: 10px;
            color: #FFFBDE;
            font-size: 1.05rem;
            line-height: 1.7;
            box-shadow: 0 0 8px rgba(106, 13, 173, 0.25);
        ">
        Enter borrower details and get an instant, AI-powered risk score with actionable strategy recommendations.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h4 style='color:#FFFBDE; margin-top:30px;'>📊 Visualize & Segment Borrowers</h4>", unsafe_allow_html=True)
        st.markdown("""
        <div style="
            background: #0B1D51;
            border: 2px solid #6a0dad;
            border-radius: 15px;
            padding: 15px;
            margin-top: 10px;
            color: #FFFBDE;
            font-size: 1.05rem;
            line-height: 1.7;
            box-shadow: 0 0 8px rgba(106, 13, 173, 0.25);
        ">
        See borrower segments, risk categories, and recommended actions in a single, easy-to-read dashboard.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h4 style='color:#FFFBDE; margin-top:30px;'>🛡️ Why You'll Love It:</h4>", unsafe_allow_html=True)

        why_blocks = [
            ("⏱ Save Time", "No more manual risk scoring - get instant, data-driven recommendations for every borrower."),
            ("💡 Actionable Insights", "Dynamic visualizations and strategy tips help you make smarter recovery decisions."),
            ("🔒 Secure & Private", "All borrower data is processed securely and never shared outside your organization.")
        ]

        for title, text in why_blocks:
            st.markdown(f"""
            <div style="
                background: #0B1D51;
                border: 2px solid #6a0dad;
                border-radius: 12px;
                padding: 15px;
                margin-top: 15px;
                color: #FFFBDE;
                font-size: 1.02rem;
                box-shadow: 0 0 10px rgba(255, 215, 0, 0.2);
            ">
            <b>{title}</b><br>{text}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
            background: #0B1D51;
            border: 2px solid #6a0dad;
            border-radius: 15px;
            padding: 20px;
            margin-top: 30px;
            color: #FFFBDE;
            font-size: 1.05rem;
            line-height: 1.8;
            box-shadow: 0 0 12px rgba(106, 13, 173, 0.3);
        ">
        <b>✔ Simple and Smooth</b><br>
        Just use the menu on the left 🧭 to explore. It's quick, secure, and designed for your workflow.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <style>
        div.stButton > button {
            background: #0B1D51;
            color: #FFFBDE;
            padding: 12px 24px;
            font-size: 1.1rem;
            border: 2px solid #f5d300;
            border-radius: 12px;
            box-shadow: 0 0 12px rgba(245, 211, 0, 0.3);
            transition: all 0.3s ease-in-out;
            width: 100%;
        }
        div.stButton > button:hover {
            background: #1a2a5c;
            color: #FFFBDE;
            transform: scale(1.03);
            border-color: #ffe600;
            cursor: pointer;
        }
        </style>
        """, unsafe_allow_html=True)

# -------------------------------
# DASHBOARD PAGE
# -------------------------------
elif page == "Smart Risk Predictor":
    with st.container():
        st.markdown(
        """
        <style>
        /* Finance-themed background for this page only */
        [data-testid="stAppViewContainer"] {
            background-image: url('https://images.unsplash.com/photo-1582139329536-e7284fece509?q=80&w=1160&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        [data-testid="stAppViewContainer"]::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(11, 29, 81, 0.40); /* #0B1D51 at 40% opacity */
            z-index: 0;
            pointer-events: none;
        }
        [data-testid="stVerticalBlock"] {
            position: relative;
            z-index: 1;
        }
        /* Custom input styling for all widgets in the predictor form */
        .custom-predictor-form label, .custom-predictor-form .stTextInput label, .custom-predictor-form .stNumberInput label, .custom-predictor-form .stSelectbox label {
            color: #FFFBDE !important;
            font-weight: 600 !important;
            font-size: 1.08em !important;
            margin-bottom: 0.25em !important;
        }
        .custom-predictor-form .stTextInput>div>div>input,
        .custom-predictor-form .stNumberInput>div>div>input,
        .custom-predictor-form .stSelectbox>div>div>div {
            color: #FFFBDE !important;
            background: rgba(11,29,81,0.92) !important;
            border: 1.5px solid #f5d300 !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            font-size: 1.08em !important;
            margin-bottom: 0.5em !important;
        }
        .custom-predictor-form .stTextInput>div>div>input:focus,
        .custom-predictor-form .stNumberInput>div>div>input:focus {
            border: 2px solid #ffe600 !important;
            outline: none !important;
        }
        .custom-predictor-form .stSelectbox>div>div>div {
            color: #FFFBDE !important;
            background: rgba(11,29,81,0.92) !important;
            border: 1.5px solid #f5d300 !important;
            border-radius: 8px !important;
            font-size: 1.08em !important;
        }
        .custom-predictor-form .stNumberInput>div>div>input[disabled] {
            color: #bdbdbd !important;
            background: rgba(11,29,81,0.45) !important;
            border: 1.5px dashed #f5d300 !important;
        }
        /* Column spacing and alignment */
        .custom-predictor-form .block-container .stColumns {
            gap: 2.5em !important;
        }
        .custom-predictor-form .stTextInput, .custom-predictor-form .stNumberInput, .custom-predictor-form .stSelectbox {
            margin-bottom: 1.1em !important;
        }
        /* Custom Predict button: #0B1D51 background, black text */
        #predict-btn div.stButton > button {
            background-color: #0B1D51 !important;
            color: #111 !important;
            border: 2px solid #f5d300;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1.1rem;
            padding: 12px 28px;
            box-shadow: 0 0 12px rgba(245, 211, 0, 0.18);
            transition: all 0.3s ease-in-out;
        }
        #predict-btn div.stButton > button:hover {
            background-color: #FFFBDE !important;
            color: #0B1D51 !important;
            border-color: #ffe600;
            transform: scale(1.04);
            cursor: pointer;
        }
        </style>
        """,
        unsafe_allow_html=True
        )


        st.markdown("""
        <h1 style="font-size: 2.8em; color: #FFFBDE; font-weight: bold; text-align: center; margin-bottom: 0.2em;">
            <span style='vertical-align:middle; margin-right:0.18em;'>
                <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" width="44" style="vertical-align:middle; margin-bottom:6px;" />
            </span>
            Smart Risk Predictor
        </h1>
        """, unsafe_allow_html=True)


        # Main input form in a semi-transparent, rounded container, now including the description and custom class
        st.markdown("""
        <div class="custom-predictor-form" style="
            background: rgba(11,29,81,0.82);
            border-radius: 18px;
            padding: 14px 10px 10px 10px;
            max-width: 700px;
            margin: 0 auto 1.2em auto;
            box-shadow: 0 4px 32px rgba(11,29,81,0.18);
            border: 2px solid #f5d300;
        ">
            <div style="
            color: #FFFBDE;
            text-align: center;
            font-size: 0.93em;
            margin-bottom: 0.7em;
            line-height: 1.35;
            letter-spacing: 0.01em;
            ">
            Instantly assess borrower risk and receive AI-powered recovery strategies tailored to each case.<br>
            Our system analyzes borrower details to predict default likelihood and recommends smart actions.<br>
            <span style="display: inline-block; margin-top: 0.3em; font-size:0.90em;">
                <b>Simply enter the borrower's information below to get started.</b>
            </span>
            </div>
        """, unsafe_allow_html=True)


        # --- Loan Type and Scheme Logic ---

        loan_type_options = ["Select Loan Type", "Personal", "Auto", "Business", "Home"]
        loan_type = st.selectbox("Select Loan Type", loan_type_options, index=0, key="loan_type_select")
        if loan_type == "Select Loan Type":
            st.info("Please select a loan type to see typical terms.")
            default_interest, default_tenure = None, None
            custom_scheme = False
        else:
            default_interest, default_tenure = get_default_loan_terms(loan_type)
            st.markdown(f"💡 **Typical Terms for a {loan_type} Loan**: `{default_interest}% interest` for `{default_tenure} months`")
            custom_scheme = st.checkbox("Loan applied during a special scheme or offer?")

        # Use columns for balanced alignment
        col1, col2 = st.columns(2, gap="large")
        with col1:
            first_name = st.text_input(
                "First Name",
                placeholder="e.g. Rahul",
                help="Enter the borrower's first name."
            )
            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"],
                index=0,
                help="Select the borrower's gender."
            )
            age = st.number_input(
                "Age",
                min_value=18, max_value=100,
                value=None,
                placeholder="e.g. 35",
                help="Enter the borrower's age (18-100)."
            )
            monthly_income = st.number_input(
                "Monthly Income (₹)",
                min_value=0.0,
                value=None,
                placeholder="e.g. 50000",
                help="Enter the borrower's monthly income in INR."
            )
            num_dependents = st.number_input(
                "Number of Dependents",
                min_value=0, step=1,
                value=None,
                placeholder="e.g. 2",
                help="Enter the number of dependents financially supported by the borrower."
            )
            loan_amount = st.number_input(
                "Loan Amount (₹)",
                min_value=10000.0,
                value=None,
                placeholder="e.g. 300000",
                help="Enter the total sanctioned loan amount in INR."
            )
            collateral_value = st.number_input(
                "Collateral Value (₹)",
                min_value=0.0,
                value=None,
                placeholder="e.g. 200000",
                help="Current value of collateral provided (if any), in INR.")
        with col2:
            last_name = st.text_input(
                "Last Name",
                placeholder="e.g. Sharma",
                help="Enter the borrower's last name."
            )
            if custom_scheme:
                interest_rate = st.number_input(
                    "Enter Custom Interest Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=default_interest,
                    step=0.1,
                    format="%.2f"
                )
                loan_tenure = st.number_input(
                    "Enter Custom Tenure (Months)",
                    min_value=1,
                    max_value=360,
                    value=default_tenure,
                    step=1
                )
            else:
                interest_rate = default_interest
                loan_tenure = default_tenure
                st.number_input(
                    "Interest Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=interest_rate,
                    disabled=True,
                    placeholder=f"{interest_rate}",
                    help="Default interest rate for selected loan type."
                )
                st.number_input(
                    "Loan Tenure (Months)",
                    min_value=1,
                    max_value=360,
                    value=loan_tenure,
                    disabled=True,
                    placeholder=f"{loan_tenure}",
                    help="Default tenure for selected loan type."
                )
            outstanding_loan = st.number_input(
                "Outstanding Loan Amount (₹)",
                min_value=0.0,
                value=None,
                placeholder="e.g. 150000",
                help="Current outstanding principal amount in INR."
            )
            # Missed Payments input
            missed_payments = st.number_input(
                "Missed Payments",
                min_value=0, step=1,
                value=None,
                placeholder="e.g. 1",
                help="Total number of missed EMI payments."
            )
            # Auto-calculate Days Past Due
            days_past_due = (missed_payments or 0) * 30
            st.number_input(
                "Days Past Due (auto)",
                value=days_past_due if missed_payments is not None else None,
                disabled=True,
                placeholder="e.g. 30",
                help="Days past due based on missed payments (1 missed payment = 30 days)."
            )
            # Auto-calculate Collection Attempts based on DPD, but 0 if missed_payments is 0
            if missed_payments == 0:
                collection_attempts = 0
            elif days_past_due <= 30:
                collection_attempts = 1
            elif 31 <= days_past_due <= 60:
                collection_attempts = 2
            elif 61 <= days_past_due <= 90:
                collection_attempts = 3
            else:
                collection_attempts = 4
            st.number_input(
                "Collection Attempts (auto)",
                value=collection_attempts if missed_payments is not None else None,
                disabled=True,
                placeholder="e.g. 1",
                help="Auto-filled based on Days Past Due (DPD)."
            )


        monthly_emi = calculate_emi(loan_amount, interest_rate, loan_tenure)
        if monthly_emi is not None:
            st.markdown(f"<div style='color:#FFFBDE; font-size:1.15em; margin-top:1em;'><b>Auto Calculated EMI:</b> ₹{monthly_emi:,.2f}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='color:#FFFBDE; font-size:1.15em; margin-top:1em;'><b>Auto Calculated EMI:</b> —</div>", unsafe_allow_html=True)

        emi_to_income = round(monthly_emi / monthly_income, 3) if (monthly_income not in (None, 0, 0.0) and monthly_emi not in (None, 0, 0.0)) else None
        collateral_coverage = round(collateral_value / loan_amount, 3) if (loan_amount not in (None, 0, 0.0) and collateral_value is not None) else None
        default_severity = missed_payments * days_past_due if (missed_payments is not None and days_past_due is not None) else None

        st.markdown("</div>", unsafe_allow_html=True)  # close input container

        # --- Helper Functions ---
        def is_missing(val):
            """Check if a required field is missing."""
            if val is None:
                return True
            if isinstance(val, str) and val.strip() == "":
                return True
            return False

        def is_invalid(val):
            """Check if value is None or NaN."""
            return val is None or (isinstance(val, float) and math.isnan(val))

        # Predict Button (scoped for custom CSS)
        with st.container():
            with st.markdown('<div id="predict-btn">', unsafe_allow_html=True):
                predict_clicked = st.button("🔐 Predict Risk & Strategy")
            st.markdown('</div>', unsafe_allow_html=True)

        if predict_clicked:
            # --- Check for Missing Inputs ---
            any_required_field_missing = (
                is_missing(first_name) or
                is_missing(last_name) or
                is_missing(age) or
                is_missing(monthly_income) or
                is_missing(num_dependents) or
                is_missing(loan_amount) or
                is_missing(loan_tenure) or
                is_missing(interest_rate) or
                is_missing(outstanding_loan) or
                is_missing(missed_payments) or
                is_missing(collateral_value)
            )

            # --- Additional Critical Calculated Value Checks ---
            if (
                any_required_field_missing or
                is_invalid(emi_to_income) or
                is_invalid(collateral_coverage) or
                is_invalid(default_severity)
            ):
                st.error("Please fill all the fields before predicting.")
                raise ValueError("Missing required fields or invalid EMI/coverage calculations.")

            # --- Edge case: Income is 0 (causes EMI/Income calc error) ---
            if monthly_income == 0:
                st.error("Monthly income cannot be zero for EMI ratio calculation.")
                raise ValueError("Invalid input: Monthly income cannot be zero.")

            input_features = np.array([[age, monthly_income, num_dependents, loan_tenure, interest_rate,
                                        outstanding_loan, collection_attempts,
                                        emi_to_income, collateral_coverage, default_severity]])

            risk_score = model.predict_proba(input_features)[0][1]
            strategy, risk_category = assign_recovery_strategy(risk_score, days_past_due)

            st.session_state['borrower_details'] = {
                'first_name': first_name,
                'last_name': last_name,
                'gender': gender,
                'age': age,
                'monthly_income': monthly_income,
                'num_dependents': num_dependents,
                'loan_amount': loan_amount,
                'loan_tenure': loan_tenure,
                'interest_rate': interest_rate,
                'outstanding_loan': outstanding_loan,
                'collection_attempts': collection_attempts,
                'missed_payments': missed_payments,
                'days_past_due': days_past_due,
                'collateral_value': collateral_value,
                'monthly_emi': monthly_emi,
                'emi_to_income': emi_to_income,
                'collateral_coverage': collateral_coverage,
                'default_severity': default_severity,
                'risk_score': risk_score,
                'risk_category': risk_category,
                'strategy': strategy
            }

            st.markdown("<hr style='border-color:#f5d300; margin: 3em 0 1.2em 0;'>", unsafe_allow_html=True)
            st.subheader("Borrower Prediction Results", divider="rainbow")

            # Assign color based on new thresholds: >0.75 red, 0.25-0.75 yellow, <0.25 green
            if risk_score > 0.75:
                risk_color = '#d32f2f'  # red
                strat_color = '#d32f2f'
            elif 0.25 <= risk_score <= 0.75:
                risk_color = '#D49B54'  # yellow
                strat_color = '#D49B54'
            else:
                risk_color = '#388e3c'  # green
                strat_color = '#388e3c'

            c1, c2 = st.columns(2)
            card_style = """
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: flex-start;
                background: rgba(245, 240, 230, 0.97);
                padding: 24px 24px 18px 24px;
                border-radius: 16px;
                border: 2px solid #0B1D51;
                min-height: 270px;
                height: 100%;
                box-sizing: border-box;
                box-shadow: 0 2px 16px rgba(11,29,81,0.10);
            """
            with c1:
                st.markdown(f"""
                    <div style='{card_style}'>
                        <h3 style='margin-bottom:0.5em;color:#0B1D51;font-weight:700;text-align:left;'>{first_name} {last_name}</h3>
                        <p style='margin-bottom:0.5em;color:#0B1D51;font-size:1.1em;'><b>Age:</b> {age} &nbsp; <b>Gender:</b> {gender}</p>
                        <p style='margin-bottom:0.5em;color:#0B1D51;font-size:1.1em;'><b>Loan Amount:</b> ₹{loan_amount:,.0f}</p>
                        <p style='margin-bottom:0.5em;color:#0B1D51;font-size:1.1em;'><b>Monthly EMI:</b> ₹{monthly_emi:,.0f}</p>
                        <p style='margin-bottom:0.5em;color:#0B1D51;font-size:1.1em;'><b>Outstanding Loan:</b> ₹{outstanding_loan:,.0f}</p>
                    </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                    <div style='{card_style} border: 2px solid {risk_color};'>
                        <div style='margin-bottom:0.25em;'>
                            <span style='display:block;color:{risk_color};font-size:1.1em;font-weight:600;'><b style='color:#0B1D51;'>Predicted Risk Score</b></span>
                            <span style='display:block;font-size:1.7em;font-weight:bold;color:{risk_color};margin-top:0.05em;margin-bottom:0.15em;text-align:left;'>{risk_score:.2%}</span>
                        </div>
                        <div style='margin-bottom:0.25em;'>
                            <span style='display:block;font-size:1.1em;'><b style='color:#0B1D51;'>Risk Category:</b> <b style='color:{risk_color}'>{risk_category}</b></span>
                        </div>
                        <div style='margin-bottom:0.15em;'>
                            <span style='display:block;color:{strat_color};font-size:1.1em;font-weight:600;'><b style='color:#0B1D51;'>Strategy</b></span>
                            <span style='display:block;margin-top:0.05em;color:{strat_color};text-align:left;font-size:1em;'>{strategy}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            risk_pct = risk_score * 100  # Recalculate for warning logic
            if 80 <= risk_pct < 85:
                st.warning("Borrower could likely enter the **Critical Zone** if any more payments are missed or compliance fails. Immediate attention recommended.")

            st.markdown("<div style='color:#FFFBDE; font-size:1.08em; margin-top:1.5em;'><b>Check insights and visualizations for this borrower by choosing the Recovery Insights page.</b></div>", unsafe_allow_html=True)

            # --- PDF Download Section ---

            import re
            def remove_emoji(text):
                # Remove most emoji and non-ASCII symbols
                return re.sub(r'[^\x00-\x7F]+', '', str(text))

            def generate_pdf(details):
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
                styles = getSampleStyleSheet()
                elements = []
                # Unique Borrower ID using new function
                borrower_id = generate_borrower_id(
                    str(details.get('loan_type', 'GEN')),
                    str(details.get('first_name', 'X')),
                    str(details.get('last_name', 'X'))
                )
                # Clean risk_category and strategy for PDF
                risk_category_clean = remove_emoji(details['risk_category'])
                strategy_clean = remove_emoji(details['strategy'])

                # Color coding logic based on risk_score (same as app)
                risk_score = details['risk_score']
                if risk_score > 0.75:
                    risk_color = '#d32f2f'  # red
                elif 0.25 <= risk_score <= 0.75:
                    risk_color = '#D49B54'  # yellow
                else:
                    risk_color = '#388e3c'  # green

                # Title
                elements.append(Paragraph("<b>Smart Loan Recovery System - Borrower Risk Report</b>", styles['Title']))
                elements.append(Spacer(1, 18))
                elements.append(Paragraph(f"<b>Borrower ID:</b> {borrower_id}", styles['Normal']))
                elements.append(Spacer(1, 8))
                # Borrower Details Table (replace ₹ with INR for PDF compatibility)
                table_data = [
                    ["Full Name", f"{details['first_name']} {details['last_name']}", "Age", details['age']],
                    ["Gender", details['gender'], "Loan Type", details.get('loan_type', '—')],
                    ["Scheme/Offer Applied?", 'Yes' if details.get('custom_scheme', False) else 'No', "Monthly Income (INR)", f"INR {details['monthly_income']:,}"],
                    ["Loan Amount (INR)", f"INR {details['loan_amount']:,}", "Outstanding Loan (INR)", f"INR {details['outstanding_loan']:,}"],
                    ["Loan Tenure (months)", details['loan_tenure'], "Interest Rate (%)", details['interest_rate']],
                    ["Collateral Value (INR)", f"INR {details['collateral_value']:,}", "Missed Payments", details['missed_payments']],
                    ["Days Past Due", details['days_past_due'], "Collection Attempts", details['collection_attempts']],
                    ["Monthly EMI (INR)", f"INR {details['monthly_emi']:,}", "EMI to Income Ratio", f"{details['emi_to_income']*100:.2f}%"],
                    ["Collateral Coverage", f"{details['collateral_coverage']*100:.2f}%", "Default Severity", details['default_severity']],
                ]
                t = Table(table_data, colWidths=[120, 120, 120, 120])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                    ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
                    ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                    ('FONTSIZE', (0,0), (-1,-1), 9),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 16))
                # Risk & Strategy (color coded)
                elements.append(Paragraph(f"<b>Predicted Risk Score:</b> <font color='{risk_color}'>{details['risk_score']*100:.2f}%</font>", styles['Normal']))
                elements.append(Paragraph(f"<b>Risk Category:</b> <font color='{risk_color}'>{risk_category_clean}</font>", styles['Normal']))
                elements.append(Spacer(1, 8))
                elements.append(Paragraph(f"<b>Recommended Strategy:</b>", styles['Normal']))
                elements.append(Paragraph(f"<font color='{risk_color}'>{strategy_clean}</font>", styles['BodyText']))
                elements.append(Spacer(1, 12))
                # Footer
                elements.append(Paragraph("<font size=8 color=grey>Generated by Smart Loan Recovery System | {}</font>".format(borrower_id), styles['Normal']))
                doc.build(elements)
                pdf = buffer.getvalue()
                buffer.close()
                return pdf, borrower_id

            # Download info line and button
            full_name = f"{first_name} {last_name}".strip()
            st.info(f"Download {full_name}'s PDF report.")
            pdf_bytes, borrower_id = generate_pdf({
                **st.session_state['borrower_details'],
                'loan_type': st.session_state.get('loan_type_select', '—'),
                'custom_scheme': st.session_state.get('custom_scheme', False)
            })
            st.download_button(
                label="Download Borrower PDF Report",
                data=pdf_bytes,
                file_name=f"borrower_report_{borrower_id}.pdf",
                mime="application/pdf",
                help="Download a professional PDF report for this borrower."
            )
    # -------------------------------
    # RECOVERY INSIGHTS
    # -------------------------------

elif page == "Recovery Insights":
    # Set risk color for border based on risk score logic
    risk_score = None
    if 'borrower_details' in st.session_state:
        risk_score = st.session_state['borrower_details'].get('risk_score', None)
    if risk_score is not None:
        risk_pct = risk_score * 100
        if risk_pct < 35:
            dashboard_border = '#388e3c'  # green
            key_color = '#388e3c'
        elif 35 <= risk_pct <= 85:
            dashboard_border = '#D49B54'  # yellow
            key_color = '#D49B54'
        else:
            dashboard_border = '#d32f2f'  # red
            key_color = '#d32f2f'
    else:
        dashboard_border = '#0B1D51'
        key_color = '#ffe600'

    # Add a graph-themed background image for Recovery Insights page
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url('https://images.unsplash.com/photo-1634117622592-114e3024ff27?q=80&w=1450&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        [data-testid="stAppViewContainer"]::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(11, 29, 81, 0.60); /* dark overlay for readability */
            z-index: 0;
            pointer-events: none;
        }}
        [data-testid="stVerticalBlock"] {{
            position: relative;
            z-index: 1;
        }}
        .dashboard-header {{
            background: linear-gradient(90deg, #0B1D51 60%, #1a2a5c 100%);
            color: {key_color};
            border-radius: 18px;
            padding: 28px 32px 18px 32px;
            margin-bottom: 2.2em;
            box-shadow: 0 4px 24px rgba(11,29,81,0.13);
            border: 2px solid {dashboard_border};
            text-align: left;
        }}
        .summary-table {{
            background: rgba(11,29,81,0.92);
            color: #FFFBDE;
            border-radius: 14px;
            border: 2px solid {dashboard_border};
            padding: 18px 18px 10px 18px;
            margin-bottom: 1.2em;
            box-shadow: 0 2px 12px rgba(11,29,81,0.10);
            font-size: 1.08em;
            width: 100%;
        }}
        .summary-table th, .summary-table td {{
            padding: 8px 14px;
            text-align: left;
            border-bottom: 1px solid #ffe60033;
        }}
        .summary-table th {{
            color: {key_color};
            font-weight: 700;
            font-size: 1.09em;
            background: rgba(245, 211, 0, 0.08);
        }}
        .summary-table td {{
            color: #FFFBDE;
        }}
        .summary-table tr:last-child td {{
            border-bottom: none;
        }}
        .dashboard-section {{
            background: rgba(11,29,81,0.80);
            border-radius: 16px;
            border: 2px solid {dashboard_border};
            padding: 12px 14px 8px 14px;
            margin-bottom: 1.2em;
            box-shadow: 0 2px 16px rgba(11,29,81,0.10);
        }}
        .dashboard-section h3 {{
            color: {key_color} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(f"""
    <div class="dashboard-header">
        <h2 style="font-size:2.2em; font-weight: bold; margin-bottom: 0.2em; color:{key_color};">📈 Recovery Insights Dashboard</h2>
        <div style="font-size:1.13em; color:{key_color}; margin-bottom:0.2em;">Borrower Risk, Strategy & Visual Analytics</div>
        <div style="font-size:1.01em; color:#FFFBDE;">All insights below are based on the most recent borrower prediction.</div>
    </div>
    """, unsafe_allow_html=True)

    if 'borrower_details' not in st.session_state:
        st.warning("No borrower prediction found. Please fill the borrower's details and predict first.")
        st.stop()

    details = st.session_state['borrower_details']

    # --- Row-wise Borrower Details Table (Minimal) ---
    # Get loan type and scheme info from session_state or fallback
    loan_type_disp = details.get('loan_type', None)
    if not loan_type_disp:
        loan_type_disp = st.session_state.get('loan_type_select', None)
    if not loan_type_disp or loan_type_disp == 'Select Loan Type':
        loan_type_disp = '—'
    scheme_disp = details.get('custom_scheme', None)
    if scheme_disp is None:
        # Try to infer from session_state
        scheme_disp = st.session_state.get('custom_scheme', False)
    scheme_disp = 'Yes' if scheme_disp else 'No'

    st.markdown(f"""
    <table class="summary-table">
        <tr><th>Full Name</th><td style='color:#FFFBDE;'>{details['first_name']} {details['last_name']}</td></tr>
        <tr><th>Age</th><td style='color:#FFFBDE;'>{details['age']}</td></tr>
        <tr><th>Gender</th><td style='color:#FFFBDE;'>{details['gender']}</td></tr>
        <tr><th>Loan Type</th><td style='color:#FFFBDE;'>{loan_type_disp}</td></tr>
        <tr><th>Scheme/Offer Applied?</th><td style='color:#FFFBDE;'>{scheme_disp}</td></tr>
        <tr><th>Loan Amount</th><td style='color:#FFFBDE;'>₹{details['loan_amount']:,}</td></tr>
        <tr><th>Monthly EMI</th><td style='color:#FFFBDE;'>₹{details['monthly_emi']:,}</td></tr>
        <tr><th>Outstanding Loan</th><td style='color:#FFFBDE;'>₹{details['outstanding_loan']:,}</td></tr>
        <tr><th>Risk Category</th><td style='color:#FFFBDE;'>{details['risk_category']}</td></tr>
        <tr><th>Strategy</th><td style='color:#FFFBDE;'>{details['strategy']}</td></tr>
    </table>
    """, unsafe_allow_html=True)

    # --- Visual Analytics Section ---
    st.markdown(f"""
    <div class='dashboard-section'>
        <h3 style='color:{key_color}; margin-bottom:0.5em; font-size:2.00em;'>Analytical Visuals & Key Metrics💡</h3>
    """, unsafe_allow_html=True)

    # --- Spread out charts: each chart full width, with spacing ---
    # 1. Bar Chart: Engineered Feature Percentages
    st.markdown("<div style='margin-bottom: 2.2em;'></div>", unsafe_allow_html=True)
    feat_bar = pd.DataFrame({
        'Feature': ['EMI to Income Ratio (%)', 'Collateral Coverage (%)'],
        'Value': [details['emi_to_income'] * 100, details['collateral_coverage'] * 100]
    })
    fig_bar = px.bar(
        feat_bar, x='Feature', y='Value', color='Feature',
        title="Engineered Feature Percentages",
        text='Value', labels={'Value': 'Percentage (%)'}
    )
    fig_bar.update_traces(texttemplate='%{text:.2f}%', textposition='inside', marker_line_width=0)
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#FFFBDE',
        title_font_color='#ffe600',
        xaxis_title='',
        yaxis_title='Percentage (%)',
        margin=dict(l=40, r=40, t=60, b=40),
        showlegend=False,
        height=420
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    st.caption(
        f"EMI to Income Ratio: {details['emi_to_income']*100:.2f}%. "
        f"Collateral Coverage: {details['collateral_coverage']*100:.2f}%. "
        "Higher EMI/Income or lower Collateral Coverage may indicate higher risk."
    )

    # 2. Donut Chart: Payment History
    st.markdown("<div style='margin-bottom: 2.2em;'></div>", unsafe_allow_html=True)
    if details['loan_tenure'] > 0:
        paid = details['loan_tenure'] - details['missed_payments']
        donut_df = pd.DataFrame({
            'Status': ['Paid', 'Missed'],
            'Count': [max(paid, 0), details['missed_payments']]
        })
        fig_donut = px.pie(
            donut_df, names='Status', values='Count',
            title="Payment History (Paid vs Missed)",
            hole=0.55, color='Status',
            color_discrete_map={'Paid': '#388e3c', 'Missed': '#d32f2f'}
        )
        fig_donut.update_traces(textinfo='percent+label+value', textfont_size=16)
        fig_donut.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#FFFBDE',
            title_font_color='#ffe600',
            margin=dict(l=40, r=40, t=60, b=40),
            height=420
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.caption(f"Missed Payments: {details['missed_payments']} out of {details['loan_tenure']} total EMIs.")

    # 3. Pie Chart: Loan vs Collateral Value
    st.markdown("<div style='margin-bottom: 2.2em;'></div>", unsafe_allow_html=True)
    total = details['loan_amount'] + details['collateral_value']
    pie_df = pd.DataFrame({
        'Type': ['Loan Amount (%)', 'Collateral Value (%)'],
        'Amount': [
            (details['loan_amount'] / total * 100) if total > 0 else 0,
            (details['collateral_value'] / total * 100) if total > 0 else 0
        ]
    })
    fig_pie = px.pie(
        pie_df, names='Type', values='Amount', title="Loan vs Collateral Value (Percentage of Total)",
        hole=0.4, color='Type',
        color_discrete_map={'Loan Amount (%)': '#0B1D51', 'Collateral Value (%)': '#ffe600'}
    )
    fig_pie.update_traces(textinfo='percent+label+value', textfont_size=16)
    fig_pie.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#FFFBDE',
        title_font_color='#ffe600',
        margin=dict(l=40, r=40, t=60, b=40),
        height=420
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    if total > 0:
        loan_pct = details['loan_amount'] / total * 100
        coll_pct = details['collateral_value'] / total * 100
        st.caption(
            f"Loan Amount: {loan_pct:.2f}%, Collateral Value: {coll_pct:.2f}% of total exposure. "
            "Higher collateral coverage reduces risk."
        )
    else:
        st.caption("No loan or collateral value entered.")

    # --- Collateral Coverage Insight ---
    if details['collateral_coverage'] < 1:
        st.warning("❗ Collateral coverage is less than 1. This means the borrower's collateral value is lower than the loan amount, which increases the lender's risk **in case of default.**")
    elif details['collateral_coverage'] == 1:
        st.info("𝒊 Collateral coverage is exactly 1. The collateral value matches the loan amount, offering basic security but little margin for error.")
    else:
        st.success("✔️ Collateral coverage is greater than 1. The borrower's collateral value exceeds the loan amount, **reducing risk for the lender.**")

    # 4. Gauge Chart: Risk Score
    st.markdown("<div style='margin-bottom: 2.2em;'></div>", unsafe_allow_html=True)
    import plotly.graph_objects as go
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = details['risk_score']*100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Predicted Risk Score (%)", 'font': {'size': 22, 'color': '#ffe600'}},
        delta = {'reference': 50, 'increasing': {'color': '#d32f2f'}, 'decreasing': {'color': '#388e3c'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': '#ffe600'},
            'bar': {'color': '#ffe600', 'thickness': 0.25},
            'bgcolor': 'rgba(11,29,81,0.85)',
            'borderwidth': 2,
            'bordercolor': '#0B1D51',
            'steps': [
                {'range': [0, 35], 'color': '#388e3c'},
                {'range': [35, 85], 'color': '#D49B54'},
                {'range': [85, 100], 'color': '#d32f2f'}
            ],
            'threshold': {
                'line': {'color': '#d32f2f', 'width': 4},
                'thickness': 0.75,
                'value': details['risk_score']*100
            }
        },
        number = {'suffix': '%', 'font': {'color': '#ffe600', 'size': 32}}
    ))
    fig_gauge.update_layout(
        margin=dict(l=40, r=40, t=80, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#FFFBDE',
        height=440
    )
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.caption(
        f"Predicted risk of default: {details['risk_score']*100:.2f}%. "
        "Higher values indicate greater likelihood of default and need for stronger recovery action."
    )

    # --- SHAP Value Visualization ---
    import shap
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np

    # --- SHAP Value Visualization ---
    try:
        # Feature names and values (must match training order)
        feature_names = [
            'Age', 'Monthly Income', 'Dependents', 'Loan Tenure', 'Interest Rate',
            'Outstanding Loan', 'Collection Attempts', 'EMI to Income',
            'Collateral Coverage', 'Default Severity'
        ]

        shap_input = pd.DataFrame([[
            details['age'],
            details['monthly_income'],
            details['num_dependents'],
            details['loan_tenure'],
            details['interest_rate'],
            details['outstanding_loan'],
            details['collection_attempts'],
            details['emi_to_income'],
            details['collateral_coverage'],
            details['default_severity']
        ]], columns=feature_names)

        # Initialize SHAP Explainer for tree-based model
        explainer = shap.TreeExplainer(model)

        # Compute SHAP values for single input row
        shap_values = explainer.shap_values(shap_input)

        # Section Heading UI (Streamlit container-style box)
        st.markdown(
            """
            <div style='background:rgba(245,240,230,0.97);border-radius:14px;padding:18px 22px 12px 22px;margin-bottom:1.2em;border:2px solid #ffe600;box-shadow:0 2px 12px rgba(11,29,81,0.10);'>
                <h3 style='color:#0B1D51;margin-bottom:0.5em;font-size:1.25em;'>🔎 SHAP Feature Impact</h3>
            """,
            unsafe_allow_html=True
        )

        # Plot SHAP waterfall (legacy compatible)
        plt.figure(figsize=(7, 3.5))
        shap.plots._waterfall.waterfall_legacy(
            explainer.expected_value,
            shap_values[0],
            feature_names=shap_input.columns.tolist(),
            max_display=10
        )
        st.pyplot(plt.gcf())
        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"⚠️ SHAP explanation failed: {e}")

    # --- Insights Summary Section ---

    st.markdown(
        """
        <div style='background:rgba(245,240,230,0.97);border-radius:14px;padding:18px 22px 12px 22px;margin-bottom:1.2em;border:2px solid #ffe600;box-shadow:0 2px 12px rgba(11,29,81,0.10);'>
            <h3 style='color:#0B1D51;margin-bottom:0.5em;font-size:1.25em;'>📝 Insights Summary</h3>
        """,
        unsafe_allow_html=True
    )

    # Dynamic insights logic
    insights = []
    # 1. EMI burden
    if details['emi_to_income'] is not None:
        if details['emi_to_income'] > 0.5:
            insights.append("EMI burden exceeds 50% of income")
        elif details['emi_to_income'] > 0.35:
            insights.append("EMI burden is moderate (35-50% of income)")
        else:
            insights.append("EMI burden is low relative to income")
    # 2. Missed payments
    if details['missed_payments'] is not None:
        if details['missed_payments'] >= 4:
            insights.append(f"Missed {details['missed_payments']} EMIs → indicates growing payment fatigue")
        elif details['missed_payments'] > 0:
            insights.append(f"Missed {details['missed_payments']} EMI{'s' if details['missed_payments']>1 else ''} recently")
        else:
            insights.append("No missed EMIs - good repayment track record")
    # 3. Collateral
    if details['collateral_value'] == 0:
        insights.append("No collateral → unsecured risk exposure")
    elif details['collateral_coverage'] is not None:
        if details['collateral_coverage'] < 1:
            insights.append("Collateral value is less than loan amount - higher risk in default")
        elif details['collateral_coverage'] == 1:
            insights.append("Collateral matches loan amount - basic security")
        else:
            insights.append("Collateral exceeds loan amount - strong security")

    # --- SHAP-based plain language insights ---
    try:
        # Get absolute SHAP values and sort by impact
        shap_impact = np.abs(shap_values[0])
        top_idx = np.argsort(shap_impact)[::-1][:3]  # Top 3 features
        for idx in top_idx:
            fname = shap_input.columns[idx]
            val = shap_input.iloc[0, idx]
            impact = shap_values[0][idx]
            # Plain language mapping for each feature
            if fname == 'EMI to Income':
                desc = "A high EMI to Income ratio means a large part of income goes to loan payments, increasing risk."
            elif fname == 'Collateral Coverage':
                desc = "Lower collateral coverage means less security for the lender, raising risk."
            elif fname == 'Missed Payments' or fname == 'Default Severity':
                desc = "More missed payments or higher default severity increases the risk of default."
            elif fname == 'Outstanding Loan':
                desc = "A higher outstanding loan amount increases the lender's exposure."
            elif fname == 'Monthly Income':
                desc = "Higher monthly income generally reduces risk, while lower income increases it."
            elif fname == 'Age':
                desc = "Borrower's age can affect risk, with very young or old ages sometimes increasing risk."
            elif fname == 'Loan Tenure':
                desc = "Longer loan tenure can increase risk due to longer exposure."
            elif fname == 'Interest Rate':
                desc = "Higher interest rates can increase repayment burden and risk."
            elif fname == 'Dependents':
                desc = "More dependents may mean higher financial obligations, increasing risk."
            elif fname == 'Collection Attempts':
                desc = "More collection attempts indicate repayment issues, raising risk."
            else:
                desc = f"Feature '{fname}' has a notable impact on risk."

            # Directional explanation
            if impact > 0:
                direction = "This increased the predicted risk."
            else:
                direction = "This helped lower the predicted risk."

            st.markdown(f"- <b>{fname}:</b> {desc} <i>{direction}</i>", unsafe_allow_html=True)
    except Exception:
        pass

    # Show only 2–3 most relevant non-SHAP insights
    for bullet in insights[:3]:
        st.markdown(f"- {bullet}")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# CONTACT US PAGE (Appended at bottom)
# -------------------------------
if 'page' in globals() and page == "Contact Us":
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    import re
    from datetime import datetime
    st.markdown("""
        <style>
        .contact-container {
            background: linear-gradient(135deg, #0B1D51 80%, #6a0dad 100%);
            border-radius: 18px;
            box-shadow: 0 4px 32px rgba(11,29,81,0.18);
            max-width: 600px;
            margin: 40px auto 0 auto;
            padding: 36px 32px 28px 32px;
            color: #FFFBDE;
        }
        .contact-header {
            color: #f5d300;
            font-size: 2.2em;
            font-weight: bold;
            text-align: center;
            margin-bottom: 18px;
            text-shadow: 0 0 8px #6a0dad44;
        }
        .contact-desc {
            color: #FFFBDE;
            font-size: 1.08em;
            text-align: center;
            margin-bottom: 22px;
        }
        /* Enhanced input styling for Contact Us form */
        .custom-contact-form label, .custom-contact-form .stTextInput label, .custom-contact-form .stTextArea label, .custom-contact-form .stSelectbox label {
            color: #f5d300 !important;
            font-weight: 700 !important;
            font-size: 1.13em !important;
            margin-bottom: 0.25em !important;
            letter-spacing: 0.01em;
        }
        .custom-contact-form .stTextInput>div>div>input,
        .custom-contact-form .stTextArea textarea,
        .custom-contact-form .stSelectbox>div>div>div {
            color: #FFFBDE !important;
            background: linear-gradient(90deg, #0B1D51 80%, #6a0dad 100%) !important;
            border: 2.5px solid #f5d300 !important;
            border-radius: 10px !important;
            padding: 10px 14px !important;
            font-size: 1.13em !important;
            margin-bottom: 0.7em !important;
            font-weight: 600 !important;
            box-shadow: 0 2px 12px rgba(245, 211, 0, 0.10);
            transition: border 0.2s, box-shadow 0.2s;
        }
        .custom-contact-form .stTextInput>div>div>input:focus,
        .custom-contact-form .stTextArea textarea:focus {
            border: 2.5px solid #ffe600 !important;
            outline: none !important;
            box-shadow: 0 0 0 2px #ffe60044;
        }
        .custom-contact-form .stSelectbox>div>div>div {
            color: #FFFBDE !important;
            background: linear-gradient(90deg, #0B1D51 80%, #6a0dad 100%) !important;
            border: 2.5px solid #f5d300 !important;
            border-radius: 10px !important;
            font-size: 1.13em !important;
            font-weight: 600 !important;
        }
        .custom-contact-form .stTextInput, .custom-contact-form .stTextArea, .custom-contact-form .stSelectbox {
            margin-bottom: 1.2em !important;
        }
        .custom-contact-form .stCheckbox>div {
            color: #f5d300 !important;
            font-weight: 600 !important;
        }
        </style>
        <div class="contact-container">
            <div class="contact-header">Contact Us</div>
            <div class="contact-desc">
                Have a question, want a demo, or need support?<br>
                Fill out the form below and I will get back to you soon.
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.form("contact_form", clear_on_submit=True):
        st.markdown('<div class="custom-contact-form">', unsafe_allow_html=True)
        st.caption("<span style='color:#ffe600;font-size:1.08em;'>All fields marked with * are required.</span>", unsafe_allow_html=True)
        fullname = st.text_input("Full Name*", placeholder="Enter your full name", help="Enter your full name as per records.")
        email = st.text_input("Business Email*", placeholder="Enter your business email", help="Enter a valid business email address.")
        org = st.text_input("Organization/Company", placeholder="Optional", help="Enter your organization or company name (optional).")
        phone = st.text_input("Phone Number", placeholder="Optional", help="Enter your phone number (optional).")
        subject = st.selectbox("Subject*", [
            "General Inquiry", "Demo Request", "Support", "Feedback", "Other"
        ], help="Select the subject of your inquiry.")
        message = st.text_area("Message*", placeholder="Type your message here...", height=120, help="Type your message or inquiry in detail.")
        consent = st.checkbox("I agree to be contacted regarding my inquiry. *Required*",
                              help="You must agree to be contacted to submit this form.")
        st.caption("<span style='color:#ffe600;font-size:1.05em;'>We respect your privacy. Your information will not be shared with third parties.</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        submitted = st.form_submit_button("➤Send Message")

        def is_valid_email(email):
            return re.match(r"[^@]+@[^@]+\.[^@]+", email)

        def is_valid_phone(phone):
            return re.match(r"^\+?\d{7,15}$", phone) if phone else True

        if submitted:
            # Check all required fields and consent
            missing_fields = []
            if not fullname:
                missing_fields.append("Full Name")
            if not email:
                missing_fields.append("Business Email")
            if not message:
                missing_fields.append("Message")
            if not consent:
                missing_fields.append("Consent")
            if missing_fields:
                st.error(f"Please fill all required fields: {', '.join(missing_fields)}.")
            elif not is_valid_email(email):
                st.error("Please enter a valid business email address.")
            elif phone and not is_valid_phone(phone):
                st.error("Please enter a valid phone number (digits only, optional +country code).")
            else:
                try:
                    # --- Google Sheets Save Logic ---
                    scope = [
                        "https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive.file",
                        "https://www.googleapis.com/auth/drive"
                    ]
                    creds = ServiceAccountCredentials.from_json_keyfile_name(
                        "Google Sheets API/glowing-sprite-465619-m7-48b1d3968bd2.json", scope
                    )
                    client = gspread.authorize(creds)
                    sheet = client.open("slrs").worksheet("Sheet1")
                    sheet.append_row([
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        fullname,
                        email,
                        org,
                        phone,
                        subject,
                        message
                    ])
                    st.success("✔ Message sent successfully! Our team will contact you soon.")
                except Exception as e:
                    st.error("✖ Oops! Something went wrong while submitting your message.")
                    st.exception(e)
        
