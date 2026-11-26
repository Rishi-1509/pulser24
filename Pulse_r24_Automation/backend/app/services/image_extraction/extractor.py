from pathlib import Path
import fitz
from app.models.schemas import VisualAsset
from app.core.config import settings
from app.services.qr_detection.detector import QRCodeDetectorService


class ImageExtractor:
    """Extracts all embedded visual assets, logos, and QR codes."""

    def __init__(self, doc: fitz.Document, doc_id: str):
        self.doc = doc
        self.doc_id = doc_id
        self.output_dir = settings.EXTRACTED_DIR / doc_id / "assets"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.qr_detector = QRCodeDetectorService()

    def extract_assets(self) -> list[VisualAsset]:
        assets: list[VisualAsset] = []
        extracted_xrefs = set()

        for pno, page in enumerate(self.doc):
            page_num = pno + 1
            image_list = page.get_images(full=True)

            for img_idx, img in enumerate(image_list):
                xref = img[0]
                if xref in extracted_xrefs:
                    continue
                extracted_xrefs.add(xref)

                try:
                    base_img = self.doc.extract_image(xref)
                    img_bytes = base_img["image"]
                    img_ext = base_img["ext"]
                    w = base_img["width"]
                    h = base_img["height"]

                    filename = f"asset_p{page_num}_{img_idx + 1}_{xref}.{img_ext}"
                    filepath = self.output_dir / filename
                    filepath.write_bytes(img_bytes)

                    # Check for QR code
                    is_qr, qr_data = self.qr_detector.decode_from_bytes(img_bytes)

                    # Classify asset
                    asset_type = "embedded_image"
                    if is_qr:
                        asset_type = "qr_code"
                    elif w >= 600 and h <= 300:
                        asset_type = "logo"
                    elif w <= 80 and h <= 80:
                        asset_type = "social_icon"
                    elif w >= 250 and h >= 200:
                        asset_type = "logo" if "logo" in filename.lower() else "news_image"

                    rel_path = f"/api/assets/{self.doc_id}/{filename}"

                    assets.append(
                        VisualAsset(
                            id=f"asset_{xref}",
                            page=page_num,
                            filename=filename,
                            rel_path=rel_path,
                            asset_type=asset_type,
                            width=w,
                            height=h,
                            size_bytes=len(img_bytes),
                            qr_decoded_data=qr_data,
                            extraction_status="extracted",
                        )
                    )
                except Exception as e:
                    continue

        return assets
