# To import, simply type: from recovery_strategy import assign_recovery_strategy

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