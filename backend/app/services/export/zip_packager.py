import io
import shutil
import zipfile
from pathlib import Path
from app.core.config import settings
from app.models.schemas import ExportManifest


class ExportPackager:
    """Packages generated email, plain text, original PDF, assets, and reports into a ZIP archive."""

    def __init__(self, doc_id: str):
        self.doc_id = doc_id
        self.doc_extracted_dir = settings.EXTRACTED_DIR / doc_id
        self.doc_generated_dir = settings.GENERATED_DIR / doc_id
        self.doc_generated_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir = settings.EXPORTS_DIR
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def create_zip_package(
        self,
        html_content: str,
        plain_text: str,
        original_pdf_path: Path,
        hyperlinks_json: str,
        hyperlinks_csv: str,
        validation_report_json: str,
    ) -> tuple[Path, ExportManifest]:
        zip_filename = f"Pulse_R24_{self.doc_id}_Email_Package.zip"
        zip_path = self.exports_dir / zip_filename

        # Save individual files to generated folder
        html_file = self.doc_generated_dir / "email.html"
        html_file.write_text(html_content, encoding="utf-8")

        txt_file = self.doc_generated_dir / "email.txt"
        txt_file.write_text(plain_text, encoding="utf-8")

        json_file = self.doc_generated_dir / "hyperlinks.json"
        json_file.write_text(hyperlinks_json, encoding="utf-8")

        csv_file = self.doc_generated_dir / "hyperlinks.csv"
        csv_file.write_text(hyperlinks_csv, encoding="utf-8")

        val_file = self.doc_generated_dir / "validation-report.json"
        val_file.write_text(validation_report_json, encoding="utf-8")

        # Instructions readme
        readme_content = """PULSE R24 EMAIL PUBLISHING STUDIO - EXPORT PACKAGE
=====================================================

Contents:
- email.html              : Complete responsive, table-based HTML email with inline CSS.
- email.txt               : Clean plain-text fallback with all sources and declarations.
- original.pdf            : Original reference PDF retained for email attachment.
- assets/                 : All extracted publication logos, images, icons, and QR codes.
- hyperlinks.json         : Complete machine-readable registry of extracted hyperlinks.
- hyperlinks.csv          : Spreadsheet-compatible source link directory.
- validation-report.json  : Comprehensive 14-point audit report.

IMPORTING INTO EMAIL SERVICE PROVIDERS (ESPs):

1. BREVO (formerly Sendinblue):
   - Navigate to Campaigns > Create an email campaign.
   - In Design section, choose 'Code your own' > 'Paste your code'.
   - Paste the contents of `email.html`.
   - In the attachments section, attach `original.pdf`.

2. MAILCHIMP:
   - Create Campaign > Email > Regular.
   - In Design Email step, select 'Code your own' > 'Paste in code'.
   - Paste the contents of `email.html`.
   - Host the images from `assets/` in your Mailchimp Content Studio or use hosted URLs.

3. EMAILOCTOPUS:
   - Campaigns > Create Campaign.
   - Choose 'Import HTML' template.
   - Upload or paste `email.html`.

4. GMAIL DRAFT WORKFLOW (Manual or future API):
   - Open Chrome, open `email.html` in browser, press Ctrl+A, Ctrl+C.
   - In Gmail compose window, paste into body.
   - Attach `original.pdf`.
   - Review draft and send.
"""

        assets_count = 0
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("email.html", html_content)
            zf.writestr("email.txt", plain_text)
            zf.writestr("hyperlinks.json", hyperlinks_json)
            zf.writestr("hyperlinks.csv", hyperlinks_csv)
            zf.writestr("validation-report.json", validation_report_json)
            zf.writestr("README.txt", readme_content)

            # Include original PDF
            if original_pdf_path.exists():
                zf.write(original_pdf_path, arcname=f"original_{original_pdf_path.name}")

            # Include assets folder
            assets_dir = self.doc_extracted_dir / "assets"
            if assets_dir.exists():
                for asset_file in assets_dir.iterdir():
                    if asset_file.is_file():
                        zf.write(asset_file, arcname=f"assets/{asset_file.name}")
                        assets_count += 1

            # Include page renders
            for page_file in self.doc_extracted_dir.glob("page_*.png"):
                zf.write(page_file, arcname=f"pages/{page_file.name}")

        manifest = ExportManifest(
            doc_id=self.doc_id,
            timestamp=html_file.stat().st_mtime.__str__(),
            html_file=f"/api/export/{self.doc_id}/email.html",
            plain_text_file=f"/api/export/{self.doc_id}/email.txt",
            original_pdf=f"/api/export/{self.doc_id}/original.pdf",
            hyperlinks_json=f"/api/export/{self.doc_id}/hyperlinks.json",
            hyperlinks_csv=f"/api/export/{self.doc_id}/hyperlinks.csv",
            validation_report_json=f"/api/export/{self.doc_id}/validation-report.json",
            zip_archive=f"/api/export/{self.doc_id}/download-zip",
            assets_included=assets_count,
        )

        return zip_path, manifest
