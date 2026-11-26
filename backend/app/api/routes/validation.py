from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.models.schemas import ValidationReport
from app.services.html_generation.generator import EmailGeneratorService
from app.services.session_manager import SessionStore
from app.services.validation.validator import ValidationEngine

router = APIRouter(prefix="/validation", tags=["validation"])


@router.post("/{doc_id}", response_model=ValidationReport)
async def validate_document(doc_id: str):
    """Run full 14-point automated pre-flight validation on document, links, assets, and email."""
    analysis = SessionStore.load_analysis(doc_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Document not found.")

    text_blocks = SessionStore.load_text_blocks(doc_id)
    hyperlinks = SessionStore.load_hyperlinks(doc_id)
    assets = SessionStore.load_assets(doc_id)
    branding = SessionStore.load_branding()

    page_images = [
        str(p)
        for p in (settings.EXTRACTED_DIR / doc_id).glob("page_*.png")
    ]
    page_images.sort()

    # Load or generate HTML to validate
    gen_file = settings.GENERATED_DIR / doc_id / "email.html"
    if gen_file.exists():
        html_content = gen_file.read_text(encoding="utf-8")
    else:
        service = EmailGeneratorService(
            doc_id=doc_id,
            text_blocks=text_blocks,
            hyperlinks=hyperlinks,
            assets=assets,
            page_images=page_images,
            branding=branding,
        )
        html_content, _ = service.generate_reconstructed_mode()

    # Find original PDF
    pdf_path = next(settings.UPLOAD_DIR.glob(f"{doc_id}_*"), Path("non_existent.pdf"))
    if not pdf_path.exists():
        pdf_path = settings.SAMPLE_DATA_DIR / "pulse_reference.pdf"

    engine = ValidationEngine(
        doc_analysis=analysis,
        text_blocks=text_blocks,
        hyperlinks=hyperlinks,
        assets=assets,
        page_images=page_images,
        html_content=html_content,
        original_pdf_path=pdf_path,
        branding=branding,
    )

    report = engine.run_all_checks()
    SessionStore.save_validation_report(doc_id, report)
    return report


@router.get("/{doc_id}", response_model=ValidationReport)
async def get_validation_report(doc_id: str):
    report = SessionStore.load_validation_report(doc_id)
    if not report:
        return await validate_document(doc_id)
    return report
