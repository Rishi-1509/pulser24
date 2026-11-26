from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, HTTPException, Response
from app.core.config import settings
from app.models.schemas import EmailGenerationRequest, EmailGenerationResponse
from app.services.html_generation.generator import EmailGeneratorService
from app.services.session_manager import SessionStore

router = APIRouter(prefix="/generate", tags=["generate"])


@router.post("/{doc_id}", response_model=EmailGenerationResponse)
async def generate_email(doc_id: str, request: EmailGenerationRequest):
    """Generate email HTML in either Faithful or Reconstructed mode."""
    analysis = SessionStore.load_analysis(doc_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Document not found.")

    text_blocks = SessionStore.load_text_blocks(doc_id)
    hyperlinks = SessionStore.load_hyperlinks(doc_id)
    assets = SessionStore.load_assets(doc_id)

    # Collect page images
    page_images = [
        str(p)
        for p in (settings.EXTRACTED_DIR / doc_id).glob("page_*.png")
    ]
    page_images.sort()

    branding = request.branding or SessionStore.load_branding()

    # Locate uploaded PDF if available (check both storage/uploads and backend/uploads)
    pdf_path = None
    upload_matches = list(settings.UPLOAD_DIR.glob(f"{doc_id}*.pdf")) + list((Path("uploads")).glob(f"{doc_id}*.pdf")) + list((Path("backend/uploads")).glob(f"{doc_id}*.pdf"))
    if upload_matches:
        pdf_path = str(upload_matches[0])

    service = EmailGeneratorService(
        doc_id=doc_id,
        text_blocks=text_blocks,
        hyperlinks=hyperlinks,
        assets=assets,
        page_images=page_images,
        branding=branding,
        base_asset_url=f"http://localhost:{settings.PORT}",
        pdf_path=pdf_path,
        embed_base64=True,
    )

    if request.mode == "faithful":
        html_out, text_out = service.generate_faithful_mode(max_width=request.max_width)
    else:
        html_out, text_out = service.generate_reconstructed_mode(max_width=request.max_width)

    # Save to generated directory
    gen_dir = settings.GENERATED_DIR / doc_id
    gen_dir.mkdir(parents=True, exist_ok=True)
    (gen_dir / f"email_{request.mode}.html").write_text(html_out, encoding="utf-8")
    (gen_dir / "email.html").write_text(html_out, encoding="utf-8")
    (gen_dir / "email.txt").write_text(text_out, encoding="utf-8")

    return EmailGenerationResponse(
        mode=request.mode,
        html_content=html_out,
        plain_text_content=text_out,
        total_links_included=len(hyperlinks),
        character_count=len(html_out),
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/preview/{doc_id}/html")
async def get_preview_html(doc_id: str, mode: str = "reconstructed"):
    """Serve the raw generated HTML with text/html content-type for sandboxed iframe preview."""
    gen_file = settings.GENERATED_DIR / doc_id / f"email_{mode}.html"
    if not gen_file.exists():
        gen_file = settings.GENERATED_DIR / doc_id / "email.html"

    if not gen_file.exists():
        # Auto-generate if not yet generated
        req = EmailGenerationRequest(mode=mode)
        await generate_email(doc_id, req)

    if gen_file.exists():
        return Response(content=gen_file.read_text(encoding="utf-8"), media_type="text/html")

    raise HTTPException(status_code=404, detail="Email HTML not generated yet.")
