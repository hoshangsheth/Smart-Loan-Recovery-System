"""Unique borrower ID generation, ported verbatim from the original app."""
import random
import string
import time


def generate_borrower_id(loan_type: str | None, first_name: str | None, last_name: str | None) -> str:
    """
    Build a borrower ID in the form `{LOANCODE}-{INITIALS}-{TIMESTAMP}-{HEX4}`.

    Matches the original `generate_borrower_id()` in slrs.py exactly, including
    its fallbacks ('GEN' for unknown loan type, 'X' for missing name parts).
    """
    loan_code = loan_type[:3].upper() if loan_type else "GEN"
    initials = (first_name[0].upper() if first_name else "X") + (last_name[0].upper() if last_name else "X")
    timestamp = str(int(time.time()))
    random_hex = "".join(random.choices(string.hexdigits.upper(), k=4))
    return f"{loan_code}-{initials}-{timestamp}-{random_hex}"
