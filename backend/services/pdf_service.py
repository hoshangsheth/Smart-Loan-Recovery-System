"""
PDF report generation service.

Structure, styling, and color logic are ported from the original
`generate_pdf()` in slrs.py. One addition per product decision: a borrower
segment row is now included, since segmentation is a new first-class
feature of this app (see services/segmentation_service.py).
"""
import re
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from repository.constants import DISPLAY_HIGH_RISK_THRESHOLD, DISPLAY_MEDIUM_RISK_THRESHOLD

RISK_COLOR_RED = "#d32f2f"
RISK_COLOR_AMBER = "#D49B54"
RISK_COLOR_GREEN = "#388e3c"


def _remove_emoji(text) -> str:
    """Strip non-ASCII symbols (emoji etc.) so ReportLab can render the text."""
    return re.sub(r"[^\x00-\x7F]+", "", str(text))


def _risk_color(risk_score: float) -> str:
    if risk_score > DISPLAY_HIGH_RISK_THRESHOLD:
        return RISK_COLOR_RED
    if DISPLAY_MEDIUM_RISK_THRESHOLD <= risk_score <= DISPLAY_HIGH_RISK_THRESHOLD:
        return RISK_COLOR_AMBER
    return RISK_COLOR_GREEN


def generate_borrower_report_pdf(report_data: dict) -> bytes:
    """
    Build the borrower risk report PDF and return it as raw bytes.

    `report_data` is expected to contain all the same keys the original
    function relied on, plus `segment_name` and `segment_description`.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    styles = getSampleStyleSheet()
    elements = []

    borrower_id = report_data["borrower_id"]
    risk_score = report_data["risk_score"]
    risk_category_clean = _remove_emoji(report_data["risk_category"])
    strategy_clean = _remove_emoji(report_data["strategy"])
    risk_color = _risk_color(risk_score)

    elements.append(Paragraph("<b>Smart Loan Recovery System - Borrower Risk Report</b>", styles["Title"]))
    elements.append(Spacer(1, 18))
    elements.append(Paragraph(f"<b>Borrower ID:</b> {borrower_id}", styles["Normal"]))
    elements.append(Spacer(1, 8))

    table_data = [
        ["Full Name", f"{report_data['first_name']} {report_data['last_name']}", "Age", report_data["age"]],
        ["Gender", report_data["gender"], "Loan Type", report_data.get("loan_type", "\u2014")],
        [
            "Scheme/Offer Applied?",
            "Yes" if report_data.get("custom_scheme", False) else "No",
            "Monthly Income (INR)",
            f"INR {report_data['monthly_income']:,.0f}",
        ],
        [
            "Loan Amount (INR)",
            f"INR {report_data['loan_amount']:,.0f}",
            "Outstanding Loan (INR)",
            f"INR {report_data['outstanding_loan']:,.0f}",
        ],
        ["Loan Tenure (months)", report_data["loan_tenure"], "Interest Rate (%)", report_data["interest_rate"]],
        [
            "Collateral Value (INR)",
            f"INR {report_data['collateral_value']:,.0f}",
            "Missed Payments",
            report_data["missed_payments"],
        ],
        ["Days Past Due", report_data["days_past_due"], "Collection Attempts", report_data["collection_attempts"]],
        [
            "Monthly EMI (INR)",
            f"INR {report_data['monthly_emi']:,.0f}",
            "EMI to Income Ratio",
            f"{report_data['emi_to_income'] * 100:.2f}%",
        ],
        [
            "Collateral Coverage",
            f"{report_data['collateral_coverage'] * 100:.2f}%",
            "Default Severity",
            report_data["default_severity"],
        ],
        ["Borrower Segment", report_data.get("segment_name", "\u2014"), "", ""],
    ]
    t = Table(table_data, colWidths=[120, 120, 120, 120])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    elements.append(t)
    elements.append(Spacer(1, 16))

    elements.append(
        Paragraph(
            f"<b>Predicted Risk Score:</b> <font color='{risk_color}'>{risk_score * 100:.2f}%</font>",
            styles["Normal"],
        )
    )
    elements.append(
        Paragraph(f"<b>Risk Category:</b> <font color='{risk_color}'>{risk_category_clean}</font>", styles["Normal"])
    )
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("<b>Recommended Strategy:</b>", styles["Normal"]))
    elements.append(Paragraph(f"<font color='{risk_color}'>{strategy_clean}</font>", styles["BodyText"]))
    elements.append(Spacer(1, 8))

    if report_data.get("segment_description"):
        elements.append(Paragraph("<b>Borrower Segment Insight:</b>", styles["Normal"]))
        elements.append(Paragraph(report_data["segment_description"], styles["BodyText"]))
        elements.append(Spacer(1, 12))
    else:
        elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            f"<font size=8 color=grey>Generated by Smart Loan Recovery System | {borrower_id}</font>",
            styles["Normal"],
        )
    )

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
