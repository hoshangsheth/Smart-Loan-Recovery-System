"""
Contact service.

Per product decision, the original Google Sheets contact form has been
removed entirely. Contact is now a direct WhatsApp deep link — this service
just builds that URL from the configured number, so the number lives in one
place (config/settings.py) rather than being hardcoded in the frontend.
"""
from config.settings import settings


def get_whatsapp_link(prefill_message: str | None = None) -> str:
    """
    Build a `wa.me` deep link, optionally pre-filling a message.

    `wa.me` links work both on mobile (opens the WhatsApp app) and desktop
    (opens WhatsApp Web), so no platform detection is needed client-side.
    """
    base = f"https://wa.me/{settings.whatsapp_number}"
    if prefill_message:
        from urllib.parse import quote

        return f"{base}?text={quote(prefill_message)}"
    return base
