"""PDF report route — streams a generated PDF back to the client."""
from fastapi import APIRouter
from fastapi.responses import Response

from api.schemas.report import ReportRequest
from services.pdf_service import generate_borrower_report_pdf

router = APIRouter(prefix="/report", tags=["report"])


@router.post("")
def download_report(payload: ReportRequest) -> Response:
    """Generate the borrower's PDF report and return it as a downloadable file."""
    pdf_bytes = generate_borrower_report_pdf(payload.model_dump())
    filename = f"borrower_report_{payload.borrower_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
