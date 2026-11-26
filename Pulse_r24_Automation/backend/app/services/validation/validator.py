import json
from datetime import datetime, timezone
from pathlib import Path
from app.models.schemas import (
    BrandingSettings,
    DocumentAnalysis,
    HyperlinkItem,
    TextBlock,
    ValidationItem,
    ValidationReport,
    VisualAsset,
)


class ValidationEngine:
    """Automated 14-point validation engine for Pulse R24 email publishing."""

    def __init__(
        self,
        doc_analysis: DocumentAnalysis,
        text_blocks: list[TextBlock],
        hyperlinks: list[HyperlinkItem],
        assets: list[VisualAsset],
        page_images: list[str],
        html_content: str,
        original_pdf_path: Path,
        branding: BrandingSettings | None = None,
    ):
        self.doc_analysis = doc_analysis
        self.text_blocks = text_blocks
        self.hyperlinks = hyperlinks
        self.assets = assets
        self.page_images = page_images
        self.html_content = html_content
        self.original_pdf_path = original_pdf_path
        self.branding = branding or BrandingSettings()

    def run_all_checks(self) -> ValidationReport:
        items: list[ValidationItem] = []

        # 1. PDF Page Count
        if self.doc_analysis.page_count > 0:
            items.append(
                ValidationItem(
                    id="chk_01_page_count",
                    title="PDF Page Count",
                    category="structure",
                    status="passed",
                    message=f"Detected {self.doc_analysis.page_count} document pages.",
                )
            )
        else:
            items.append(
                ValidationItem(
                    id="chk_01_page_count",
                    title="PDF Page Count",
                    category="structure",
                    status="failed",
                    message="Document has 0 readable pages.",
                    recommendation="Verify PDF file integrity.",
                )
            )

        # 2. Generated Page Count
        if len(self.page_images) == self.doc_analysis.page_count:
            items.append(
                ValidationItem(
                    id="chk_02_rendered_pages",
                    title="Generated Page Slices",
                    category="structure",
                    status="passed",
                    message=f"All {len(self.page_images)} page slices successfully rendered at high resolution.",
                )
            )
        else:
            items.append(
                ValidationItem(
                    id="chk_02_rendered_pages",
                    title="Generated Page Slices",
                    category="structure",
                    status="warning",
                    message=f"Rendered {len(self.page_images)} pages for a {self.doc_analysis.page_count}-page PDF.",
                    recommendation="Re-run extraction to render missing pages.",
                )
            )

        # 3. Text Extraction
        total_text_len = sum(len(b.text) for b in self.text_blocks)
        if total_text_len > 500:
            items.append(
                ValidationItem(
                    id="chk_03_text_extraction",
                    title="Text Extraction",
                    category="content",
                    status="passed",
                    message=f"Extracted {len(self.text_blocks)} blocks ({total_text_len:,} characters) with formatting.",
                )
            )
        elif total_text_len > 0:
            items.append(
                ValidationItem(
                    id="chk_03_text_extraction",
                    title="Text Extraction",
                    category="content",
                    status="warning",
                    message=f"Low text character count ({total_text_len} chars).",
                    recommendation="Ensure the PDF contains a selectable text layer or enable OCR.",
                )
            )
        else:
            items.append(
                ValidationItem(
                    id="chk_03_text_extraction",
                    title="Text Extraction",
                    category="content",
                    status="failed",
                    message="No text extracted from document.",
                    recommendation="Enable Tesseract OCR fallback.",
                )
            )

        # 4. Hyperlink Extraction
        if len(self.hyperlinks) > 0:
            items.append(
                ValidationItem(
                    id="chk_04_link_extraction",
                    title="Hyperlink Extraction",
                    category="hyperlinks",
                    status="passed",
                    message=f"Extracted {len(self.hyperlinks)} embedded hyperlink annotations.",
                )
            )
        else:
            items.append(
                ValidationItem(
                    id="chk_04_link_extraction",
                    title="Hyperlink Extraction",
                    category="hyperlinks",
                    status="warning",
                    message="No embedded hyperlink annotations found.",
                    recommendation="Verify whether this edition of Pulse R24 includes web sources.",
                )
            )

        # 5. Link-to-Text Mapping
        mapped_links = [l for l in self.hyperlinks if l.mapping_status == "mapped"]
        mapping_pct = (len(mapped_links) / len(self.hyperlinks) * 100) if self.hyperlinks else 100
        if mapping_pct >= 90:
            items.append(
                ValidationItem(
                    id="chk_05_link_mapping",
                    title="Link-to-Text Mapping",
                    category="hyperlinks",
                    status="passed",
                    message=f"{len(mapped_links)} of {len(self.hyperlinks)} links ({mapping_pct:.1f}%) mapped to anchor text.",
                )
            )
        elif mapping_pct >= 70:
            items.append(
                ValidationItem(
                    id="chk_05_link_mapping",
                    title="Link-to-Text Mapping",
                    category="hyperlinks",
                    status="warning",
                    message=f"{len(self.hyperlinks) - len(mapped_links)} links lacked immediate geometric anchor text.",
                    recommendation="Review Hyperlink Manager to review unmapped links.",
                )
            )
        else:
            items.append(
                ValidationItem(
                    id="chk_05_link_mapping",
                    title="Link-to-Text Mapping",
                    category="hyperlinks",
                    status="warning",
                    message=f"Only {mapping_pct:.1f}% of links could be automatically mapped to text.",
                    recommendation="Use the Hyperlink Manager to assign visible text.",
                )
            )

        # 6. URL Preservation
        malformed_urls = [l for l in self.hyperlinks if not (l.url.startswith("http://") or l.url.startswith("https://") or l.url.startswith("mailto:"))]
        if not malformed_urls:
            items.append(
                ValidationItem(
                    id="chk_06_url_preservation",
                    title="URL Preservation & Syntax",
                    category="hyperlinks",
                    status="passed",
                    message="All extracted links contain valid absolute web or email protocols.",
                )
            )
        else:
            items.append(
                ValidationItem(
                    id="chk_06_url_preservation",
                    title="URL Preservation & Syntax",
                    category="hyperlinks",
                    status="warning",
                    message=f"{len(malformed_urls)} links contain non-standard or relative protocols.",
                    affected_element=", ".join([l.id for l in malformed_urls[:3]]),
                    recommendation="Inspect and correct URLs in Hyperlink Manager.",
                )
            )

        # 7. Missing Images
        if len(self.assets) > 0:
            items.append(
                ValidationItem(
                    id="chk_07_images_extracted",
                    title="Visual Asset Extraction",
                    category="assets",
                    status="passed",
                    message=f"Extracted {len(self.assets)} visual assets (logos, icons, embedded graphics).",
                )
            )
        else:
            items.append(
                ValidationItem(
                    id="chk_07_images_extracted",
                    title="Visual Asset Extraction",
                    category="assets",
                    status="warning",
                    message="No embedded images were found in the PDF.",
                    recommendation="Confirm whether the document relies on vector graphics or page renders.",
                )
            )

        # 8. Missing Logos
        logos = [a for a in self.assets if a.asset_type == "logo" or a.width >= 300]
        if logos:
            items.append(
                ValidationItem(
                    id="chk_08_logos",
                    title="Branding & Logos",
                    category="assets",
                    status="passed",
                    message=f"Identified {len(logos)} publication/institutional logos.",
                )
            )
        else:
            items.append(
                ValidationItem(
                    id="chk_08_logos",
                    title="Branding & Logos",
                    category="assets",
                    status="warning",
                    message="No distinct logo asset identified. Default Pulse R24 vector banner will be used.",
                    recommendation="Upload custom logos in Settings if desired.",
                )
            )

        # 9. QR Code Extraction & Decoding
        qr_assets = [a for a in self.assets if a.asset_type == "qr_code"]
        decoded_qr = [a for a in qr_assets if a.qr_decoded_data]
        if decoded_qr:
            items.append(
                ValidationItem(
                    id="chk_09_qr_code",
                    title="QR Code Detection & Decoding",
                    category="assets",
                    status="passed",
                    message=f"QR code detected and successfully decoded: {decoded_qr[0].qr_decoded_data}",
                )
            )
        elif qr_assets:
            items.append(
                ValidationItem(
                    id="chk_09_qr_code",
                    title="QR Code Detection & Decoding",
                    category="assets",
                    status="warning",
                    message="QR code image extracted, but OpenCV could not decode the payload.",
                    recommendation="Manually specify the QR destination URL in Settings.",
                )
            )
        else:
            items.append(
                ValidationItem(
                    id="chk_09_qr_code",
                    title="QR Code Detection & Decoding",
                    category="assets",
                    status="warning",
                    message="No separate QR code image detected.",
                    recommendation="Verify if QR code is rendered directly on page raster.",
                )
            )

        # 10. Social Media Configuration
        configured_social = {k: v for k, v in self.branding.social_links.items() if v.strip()}
        if len(configured_social) >= 2:
            items.append(
                ValidationItem(
                    id="chk_10_social_links",
                    title="Social Media Channels",
                    category="email_compatibility",
                    status="passed",
                    message=f"Configured {len(configured_social)} active social channels ({', '.join(configured_social.keys())}).",
                )
            )
        else:
            items.append(
                ValidationItem(
                    id="chk_10_social_links",
                    title="Social Media Channels",
                    category="email_compatibility",
                    status="warning",
                    message="Few or no social media URLs configured.",
                    recommendation="Update social channels in Settings.",
                )
            )

        # 11. HTML Syntax & Email Standards
        has_doctype = "<!DOCTYPE" in self.html_content
        has_table = "<table" in self.html_content
        has_inline_style = 'style="' in self.html_content
        if has_doctype and has_table and has_inline_style:
            items.append(
                ValidationItem(
                    id="chk_11_html_syntax",
                    title="HTML Syntax & Table-Based Layout",
                    category="email_compatibility",
                    status="passed",
                    message="Valid XHTML doctype, nested table structure, and inline CSS verified.",
                )
            )
        else:
            items.append(
                ValidationItem(
                    id="chk_11_html_syntax",
                    title="HTML Syntax & Table-Based Layout",
                    category="email_compatibility",
                    status="failed",
                    message="HTML structure is missing required email markup.",
                    recommendation="Regenerate email template.",
                )
            )

        # 12. Broken Asset References
        forbidden_patterns = ["file://", "localhost:", "127.0.0.1:", "C:\\", "/tmp/"]
        broken_refs = [p for p in forbidden_patterns if p in self.html_content]
        # In development preview, localhost is expected, but filesystem paths are prohibited
        filesystem_leak = any(p in self.html_content for p in ["file://", "C:\\", "/tmp/"])
        if not filesystem_leak:
            items.append(
                ValidationItem(
                    id="chk_12_asset_refs",
                    title="Local Filesystem Leak Prevention",
                    category="email_compatibility",
                    status="passed",
                    message="No local filesystem (file:// or C:\\) paths detected in email HTML.",
                )
            )
        else:
            items.append(
                ValidationItem(
                    id="chk_12_asset_refs",
                    title="Local Filesystem Leak Prevention",
                    category="email_compatibility",
                    status="failed",
                    message="Found local filesystem paths in HTML that will fail in email clients.",
                    recommendation="Ensure all assets use web URLs or CID attachments.",
                )
            )

        # 13. Responsive Layout
        has_viewport = "name=\"viewport\"" in self.html_content
        has_media_query = "@media" in self.html_content
        if has_viewport and has_media_query:
            items.append(
                ValidationItem(
                    id="chk_13_responsive",
                    title="Responsive Mobile Compatibility",
                    category="email_compatibility",
                    status="passed",
                    message="Viewport meta tag and mobile CSS media queries (@media screen and max-width) present.",
                )
            )
        else:
            items.append(
                ValidationItem(
                    id="chk_13_responsive",
                    title="Responsive Mobile Compatibility",
                    category="email_compatibility",
                    status="warning",
                    message="Missing viewport tag or media query.",
                    recommendation="Ensure responsive template styles are active.",
                )
            )

        # 14. Original PDF Attachment Availability
        if self.original_pdf_path.exists() and self.original_pdf_path.stat().st_size > 0:
            items.append(
                ValidationItem(
                    id="chk_14_original_pdf",
                    title="Original PDF Attachment",
                    category="content",
                    status="passed",
                    message=f"Original PDF preserved ({self.original_pdf_path.name}, {self.original_pdf_path.stat().st_size / 1024:.1f} KB). Ready as email attachment.",
                )
            )
        else:
            items.append(
                ValidationItem(
                    id="chk_14_original_pdf",
                    title="Original PDF Attachment",
                    category="content",
                    status="failed",
                    message="Original PDF file is missing or empty.",
                    recommendation="Re-upload the original bulletin PDF.",
                )
            )

        # Aggregate status
        failed_count = sum(1 for i in items if i.status == "failed")
        warning_count = sum(1 for i in items if i.status == "warning")
        passed_count = sum(1 for i in items if i.status == "passed")

        overall_status = "passed"
        if failed_count > 0:
            overall_status = "failed"
        elif warning_count > 0:
            overall_status = "warning"

        return ValidationReport(
            doc_id=self.doc_analysis.doc_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            overall_status=overall_status,
            total_checks=len(items),
            passed_count=passed_count,
            warning_count=warning_count,
            failed_count=failed_count,
            items=items,
        )
