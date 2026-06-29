"""Contact route — returns the WhatsApp deep link for the frontend's contact button."""
from fastapi import APIRouter

from services.contact_service import get_whatsapp_link

router = APIRouter(prefix="/contact", tags=["contact"])


@router.get("/whatsapp-link")
def whatsapp_link() -> dict:
    """Return the configured WhatsApp contact link."""
    return {"url": get_whatsapp_link()}
