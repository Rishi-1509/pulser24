import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile
from app.core.config import settings
from app.models.schemas import DocumentAnalysis, TextBlock
from app.services.hyperlink_extraction.extractor import HyperlinkExtractor
from app.services.image_extraction.extractor import ImageExtractor
from app.services.pdf_extraction.extractor import PDFExtractor
from app.services.session_manager import SessionStore

router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.post("/upload", response_model=DocumentAnalysis)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a new Pulse R24 newsletter PDF and trigger automatic analysis."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    doc_id = str(uuid.uuid4())[:8]
    clean_filename = Path(file.filename).name
    save_path = settings.UPLOAD_DIR / f"{doc_id}_{clean_filename}"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return await _process_pdf(save_path, doc_id)


@router.post("/analyze-reference", response_model=DocumentAnalysis)
async def analyze_reference():
    """Analyze the staged reference PDF (Issue 359) immediately."""
    ref_pdf = settings.SAMPLE_DATA_DIR / "pulse_reference.pdf"
    if not ref_pdf.exists():
        # Check parent folder
        fallback = settings.BASE_DIR / "PULSE_RELEASE_2026-11-25_edition.pdf"
        if fallback.exists():
            shutil.copy(fallback, ref_pdf)
        else:
            raise HTTPException(status_code=404, detail="Reference PDF not found in sample-data.")

    doc_id = "ref_359"
    dest_path = settings.UPLOAD_DIR / f"{doc_id}_pulse_reference.pdf"
    shutil.copy(ref_pdf, dest_path)
    return await _process_pdf(dest_path, doc_id)


async def _process_pdf(pdf_path: Path, doc_id: str) -> DocumentAnalysis:
    """Full extraction pipeline."""
    extractor = PDFExtractor(pdf_path=pdf_path, doc_id=doc_id)
    analysis = extractor.extract_metadata()
    page_images = extractor.render_page_images(dpi=150)
    text_blocks = extractor.extract_text_blocks()

    # Extract hyperlinks
    link_extractor = HyperlinkExtractor(extractor.doc)
    hyperlinks = link_extractor.extract_hyperlinks()

    # Extract assets & QR
    image_extractor = ImageExtractor(extractor.doc, doc_id=doc_id)
    assets = image_extractor.extract_assets()

    # QR Detection status
    qr_asset = next((a for a in assets if a.asset_type == "qr_code"), None)

    analysis.total_hyperlinks = len(hyperlinks)
    analysis.mapped_hyperlinks = sum(1 for l in hyperlinks if l.mapping_status == "mapped")
    analysis.total_images = len(assets)
    analysis.text_blocks_count = len(text_blocks)
    if qr_asset:
        analysis.qr_detected = True
        analysis.qr_content = qr_asset.qr_decoded_data

    # Persist all data in SessionStore
    SessionStore.save_analysis(doc_id, analysis)
    SessionStore.save_text_blocks(doc_id, text_blocks)
    SessionStore.save_hyperlinks(doc_id, hyperlinks)
    SessionStore.save_assets(doc_id, assets)

    return analysis


@router.get("/documents", response_model=list[DocumentAnalysis])
async def list_documents():
    """List all analyzed documents stored in session."""
    docs = []
    if settings.EXTRACTED_DIR.exists():
        for d in settings.EXTRACTED_DIR.iterdir():
            if d.is_dir():
                meta = SessionStore.load_analysis(d.name)
                if meta:
                    docs.append(meta)
    return docs


@router.get("/documents/{doc_id}", response_model=DocumentAnalysis)
async def get_document(doc_id: str):
    analysis = SessionStore.load_analysis(doc_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Document not found.")
    return analysis


@router.get("/documents/{doc_id}/text-blocks", response_model=list[TextBlock])
async def get_text_blocks(doc_id: str):
    blocks = SessionStore.load_text_blocks(doc_id)
    return blocks
