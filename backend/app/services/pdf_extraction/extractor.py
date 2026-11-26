import os
import uuid
from pathlib import Path
import fitz
from app.models.schemas import BoundingBox, DocumentAnalysis, TextBlock
from app.core.config import settings


class PDFExtractor:
    """Extracts text blocks, metadata, page dimensions, and high-res page images."""

    def __init__(self, pdf_path: str | Path, doc_id: str | None = None):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {self.pdf_path}")
        self.doc_id = doc_id or str(uuid.uuid4())[:8]
        self.doc = fitz.open(str(self.pdf_path))
        self.output_dir = settings.EXTRACTED_DIR / self.doc_id
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_metadata(self) -> DocumentAnalysis:
        meta = self.doc.metadata or {}
        stat = self.pdf_path.stat()
        page_dims = []

        for pno, page in enumerate(self.doc):
            rect = page.rect
            page_dims.append({
                "page": pno + 1,
                "width": round(rect.width, 2),
                "height": round(rect.height, 2),
            })

        return DocumentAnalysis(
            doc_id=self.doc_id,
            filename=self.pdf_path.name,
            file_size_bytes=stat.st_size,
            page_count=len(self.doc),
            title=meta.get("title") or self.pdf_path.stem,
            author=meta.get("author") or "Pulse R24 Editorial Desk",
            created_at=meta.get("creationDate") or "",
            page_dimensions=page_dims,
        )

    def render_page_images(self, dpi: int = 150) -> list[str]:
        """Render each page to high-res PNG for Faithful Mode and visual inspection."""
        rendered_paths = []
        for pno, page in enumerate(self.doc):
            pix = page.get_pixmap(dpi=dpi)
            img_filename = f"page_{pno + 1}.png"
            img_path = self.output_dir / img_filename
            pix.save(str(img_path))
            rendered_paths.append(str(img_path))
        return rendered_paths

    def extract_text_blocks(self) -> list[TextBlock]:
        """Extract text blocks with font properties and bounding boxes."""
        blocks: list[TextBlock] = []

        for pno, page in enumerate(self.doc):
            page_num = pno + 1
            # Use raw textpage dict to get spans with font size and flags
            text_dict = page.get_text("dict")
            for b_idx, block in enumerate(text_dict.get("blocks", [])):
                if block.get("type") == 0:  # text block
                    full_text = []
                    font_sizes = []
                    font_names = []
                    is_bold = False

                    for line in block.get("lines", []):
                        line_text = ""
                        for span in line.get("spans", []):
                            txt = span.get("text", "")
                            line_text += txt
                            font_sizes.append(span.get("size", 10.0))
                            font_names.append(span.get("font", ""))
                            flags = span.get("flags", 0)
                            if flags & 2 != 0 or "Bold" in span.get("font", "") or "bold" in span.get("font", ""):
                                is_bold = True
                        if line_text.strip():
                            full_text.append(line_text)

                    merged_text = "\n".join(full_text).strip()
                    if not merged_text:
                        continue

                    avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 10.0
                    dominant_font = font_names[0] if font_names else "Arial"

                    # Classify block type based on font size and formatting
                    is_headline = avg_font_size >= 13.0 or (avg_font_size >= 11.5 and is_bold)
                    block_type = "paragraph"
                    if avg_font_size >= 16.0:
                        block_type = "headline"
                    elif avg_font_size >= 12.0 and is_bold:
                        block_type = "subheading"
                    elif avg_font_size <= 7.5 or "Disclaimer" in merged_text or "ISSN" in merged_text:
                        block_type = "footer"
                    elif "Source:" in merged_text or "Ref:" in merged_text:
                        block_type = "citation"

                    bbox_raw = block.get("bbox", [0, 0, 0, 0])
                    blocks.append(
                        TextBlock(
                            id=f"p{page_num}_b{b_idx}",
                            page=page_num,
                            text=merged_text,
                            font_name=dominant_font,
                            font_size=round(avg_font_size, 1),
                            is_bold=is_bold,
                            is_headline=is_headline,
                            bbox=BoundingBox(
                                x0=round(bbox_raw[0], 2),
                                y0=round(bbox_raw[1], 2),
                                x1=round(bbox_raw[2], 2),
                                y1=round(bbox_raw[3], 2),
                            ),
                            block_type=block_type,
                        )
                    )

        # Fallback OCR if no text found
        if not blocks:
            blocks = self._ocr_fallback()

        return blocks

    def _ocr_fallback(self) -> list[TextBlock]:
        """Tesseract OCR fallback if PDF lacks native text stream."""
        blocks: list[TextBlock] = []
        try:
            import pytesseract
            from PIL import Image

            if settings.TESSERACT_CMD:
                pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

            for pno, page in enumerate(self.doc):
                pix = page.get_pixmap(dpi=200)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                ocr_text = pytesseract.image_to_string(img)
                if ocr_text.strip():
                    blocks.append(
                        TextBlock(
                            id=f"p{pno+1}_ocr",
                            page=pno + 1,
                            text=ocr_text.strip(),
                            font_name="OCR_Fallback",
                            font_size=10.0,
                            is_bold=False,
                            is_headline=False,
                            bbox=BoundingBox(x0=0, y0=0, x1=pix.width, y1=pix.height),
                            block_type="paragraph",
                        )
                    )
        except Exception:
            pass
        return blocks
