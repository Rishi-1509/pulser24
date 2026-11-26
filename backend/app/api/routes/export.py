from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.core.config import settings
from app.models.schemas import ExportManifest
from app.services.export.zip_packager import ExportPackager
from app.services.html_generation.generator import EmailGeneratorService
from app.services.hyperlink_extraction.extractor import HyperlinkExtractor
from app.services.session_manager import SessionStore

router = APIRouter(prefix="/export", tags=["export"])


@router.post("/{doc_id}/package", response_model=ExportManifest)
async def create_export_package(doc_id: str):
    """Generate final email files, reports, assets and package them into a downloadable ZIP."""
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

    service = EmailGeneratorService(
        doc_id=doc_id,
        text_blocks=text_blocks,
        hyperlinks=hyperlinks,
        assets=assets,
        page_images=page_images,
        branding=branding,
    )
    html_out, text_out = service.generate_reconstructed_mode()

    # Find original PDF
    pdf_path = next(settings.UPLOAD_DIR.glob(f"{doc_id}_*"), Path("non_existent.pdf"))
    if not pdf_path.exists():
        pdf_path = settings.SAMPLE_DATA_DIR / "pulse_reference.pdf"

    # Validation report
    report = SessionStore.load_validation_report(doc_id)
    val_json = report.model_dump_json(indent=2) if report else "{}"

    packager = ExportPackager(doc_id=doc_id)
    zip_path, manifest = packager.create_zip_package(
        html_content=html_out,
        plain_text=text_out,
        original_pdf_path=pdf_path,
        hyperlinks_json=HyperlinkExtractor.export_to_json(hyperlinks),
        hyperlinks_csv=HyperlinkExtractor.export_to_csv(hyperlinks),
        validation_report_json=val_json,
    )

    return manifest


@router.get("/{doc_id}/download-zip")
async def download_zip(doc_id: str):
    """Download the complete ZIP package."""
    zip_path = settings.EXPORTS_DIR / f"Pulse_R24_{doc_id}_Email_Package.zip"
    if not zip_path.exists():
        # Auto-create if not generated
        await create_export_package(doc_id)

    if zip_path.exists():
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=zip_path.name,
        )
    raise HTTPException(status_code=404, detail="Export package not found.")


@router.get("/{doc_id}/{filename}")
async def download_file(doc_id: str, filename: str):
    """Download an individual generated file (email.html, email.txt, original.pdf, etc.)."""
    if filename == "original.pdf":
        pdf_path = next(settings.UPLOAD_DIR.glob(f"{doc_id}_*"), None)
        if not pdf_path or not pdf_path.exists():
            pdf_path = settings.SAMPLE_DATA_DIR / "pulse_reference.pdf"
        return FileResponse(pdf_path, media_type="application/pdf", filename=f"pulse_original_{doc_id}.pdf")

    file_path = settings.GENERATED_DIR / doc_id / filename
    if file_path.exists():
        media_type = "text/plain"
        if filename.endswith(".html"):
            media_type = "text/html"
        elif filename.endswith(".json"):
            media_type = "application/json"
        elif filename.endswith(".csv"):
            media_type = "text/csv"

        return FileResponse(file_path, media_type=media_type, filename=filename)

    raise HTTPException(status_code=404, detail=f"File {filename} not found.")
