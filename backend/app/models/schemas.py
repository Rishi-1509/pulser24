from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class TextBlock(BaseModel):
    id: str
    page: int
    text: str
    font_name: str | None = None
    font_size: float = 10.0
    is_bold: bool = False
    is_headline: bool = False
    bbox: BoundingBox
    block_type: str = "paragraph"  # headline, subheading, paragraph, footer, citation, table


class HyperlinkItem(BaseModel):
    id: str
    page: int
    url: str
    visible_text: str
    bbox: BoundingBox
    link_type: str = "external"  # external, internal, email
    mapping_status: Literal["mapped", "unmapped", "manual", "flagged"] = "mapped"
    context_text: str = ""
    is_verified: bool | None = None


class HyperlinkUpdateRequest(BaseModel):
    visible_text: str | None = None
    url: str | None = None
    mapping_status: Literal["mapped", "unmapped", "manual", "flagged"] | None = None


class VisualAsset(BaseModel):
    id: str
    page: int
    filename: str
    rel_path: str
    asset_type: Literal["logo", "qr_code", "social_icon", "news_image", "page_render", "embedded_image"]
    width: int
    height: int
    size_bytes: int
    qr_decoded_data: str | None = None
    extraction_status: str = "extracted"


class BrandingSettings(BaseModel):
    app_title: str = "Pulse R24 Email Publishing Studio"
    bulletin_name: str = "PULSE R24"
    primary_color: str = "#0f2d59"  # Deep Navy Pulse brand
    secondary_color: str = "#2563eb"
    accent_color: str = "#d97706"
    font_family: str = "Arial, Helvetica, sans-serif"
    max_email_width: int = 650
    social_links: dict[str, str] = Field(
        default_factory=lambda: {
            "x_twitter": "https://twitter.com/issp_india",
            "linkedin": "https://www.linkedin.com/company/issp-india",
            "youtube": "https://www.youtube.com/@issp_india",
            "website": "https://rru.ac.in",
        }
    )
    ai_declaration: str = (
        "AI Declaration: This publication incorporates automated collection and AI-assisted "
        "compilation. All links, sources, and factual narratives have been deterministic-extracted "
        "and human-reviewed."
    )
    institutional_attribution: str = (
        "Published by the Center for Security & Intelligence Studies in collaboration with "
        "ISSP, RRU Puducherry, and CAREVIA."
    )


class DocumentAnalysis(BaseModel):
    doc_id: str
    filename: str
    file_size_bytes: int
    page_count: int
    title: str | None = None
    author: str | None = None
    created_at: str
    page_dimensions: list[dict] = Field(default_factory=list)
    total_hyperlinks: int = 0
    mapped_hyperlinks: int = 0
    total_images: int = 0
    qr_detected: bool = False
    qr_content: str | None = None
    text_blocks_count: int = 0


class EmailGenerationRequest(BaseModel):
    mode: Literal["faithful", "reconstructed"] = "reconstructed"
    include_source_directory: bool = True
    branding: BrandingSettings | None = None
    max_width: int = 650


class EmailGenerationResponse(BaseModel):
    mode: str
    html_content: str
    plain_text_content: str
    total_links_included: int
    character_count: int
    generated_at: str


class ValidationItem(BaseModel):
    id: str
    title: str
    category: str  # content, hyperlinks, assets, email_compatibility, structure
    status: Literal["passed", "warning", "failed"]
    message: str
    affected_page: int | None = None
    affected_element: str | None = None
    recommendation: str | None = None


class ValidationReport(BaseModel):
    doc_id: str
    timestamp: str
    overall_status: Literal["passed", "warning", "failed"]
    total_checks: int
    passed_count: int
    warning_count: int
    failed_count: int
    items: list[ValidationItem]


class ExportManifest(BaseModel):
    doc_id: str
    timestamp: str
    html_file: str
    plain_text_file: str
    original_pdf: str
    hyperlinks_json: str
    hyperlinks_csv: str
    validation_report_json: str
    zip_archive: str
    assets_included: int
