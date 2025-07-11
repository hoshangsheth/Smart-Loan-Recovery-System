Smart Loan Recovery System
=========================

A professional Streamlit dashboard for loan risk assessment, borrower analytics, and AI-powered recovery strategy recommendations. Includes robust UI/UX, PDF report generation, model explainability, and a business-grade contact form with Google Sheets integration.

Features
--------
- Smart Risk Predictor: Enter borrower details to predict risk of default and receive tailored recovery strategies. Auto-calculated fields (EMI, DPD, Collection Attempts, etc.). Robust validation (0 is valid for all fields). Professional, color-coded PDF report download with unique borrower ID. User-friendly error handling (no Python tracebacks).

- Recovery Insights Dashboard: Visualizes borrower details, risk, and strategy in a modern dashboard. Analytical charts: EMI/Income, Collateral Coverage, Payment History, Risk Gauge. SHAP value visualization for model explainability. Dynamic, plain-language Insights Summary (SHAP + business logic). Graph-themed background for visual appeal.

- Contact Us: Business-grade contact form with required field and consent validation. Google Sheets integration for message storage. Custom-styled input fields matching app branding.

- Branding & UI: Custom sidebar and header with Flaticon icons. Modern, responsive CSS and layout.

Setup Instructions
------------------
1. Clone the repository or copy the project files.
2. Install dependencies:
   pip install -r requirements.txt
3. Google Sheets Integration:
   - Place your Google Service Account JSON key in 'Google Sheets API/' (update filename in code if needed).
   - Share your target Google Sheet with the service account email.
4. Run the app:
   streamlit run app1.py
5. Usage:
   - Use the sidebar to navigate between Smart Risk Predictor, Recovery Insights, and Contact Us.
   - Fill in borrower details and click Predict to view results and download the PDF report.
   - View analytics and SHAP explanations in Recovery Insights.
   - Use Contact Us for support, demo requests, or feedback.

File Structure
--------------
- slrs.py — Main Streamlit app
- requirements.txt — Python dependencies
- Google Sheets API/ — Service account JSON for Google Sheets
- Notebooks & Strategy/, PKL Files/ — Model and feature files
- Dataset/ — Sample data
- Project Documents/ — Notes and workflow docs

Model & Explainability
---------------------
- XGBoost model for risk prediction (pickle file required)
- SHAP for model explainability (waterfall plot and plain-language insights)

PDF Reports
-----------
- Downloadable, color-coded, professional PDF for each borrower
- Unique, robust borrower ID (no emoji or unsupported symbols)

Contact & Support
-----------------
- Contact form messages are saved to Google Sheets for follow-up
- All required fields and consent are validated

Author: Hoshang Sheth
For questions, support, or demo requests, use the Contact Us page in the app.
