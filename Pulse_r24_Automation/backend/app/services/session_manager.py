import json
from pathlib import Path
from app.core.config import settings
from app.models.schemas import (
    BrandingSettings,
    DocumentAnalysis,
    HyperlinkItem,
    TextBlock,
    ValidationReport,
    VisualAsset,
)


class SessionStore:
    """Persists document analysis, links, text blocks, and settings to disk."""

    @staticmethod
    def get_doc_dir(doc_id: str) -> Path:
        p = settings.EXTRACTED_DIR / doc_id
        p.mkdir(parents=True, exist_ok=True)
        return p

    @classmethod
    def save_analysis(cls, doc_id: str, analysis: DocumentAnalysis):
        f = cls.get_doc_dir(doc_id) / "analysis.json"
        f.write_text(analysis.model_dump_json(indent=2), encoding="utf-8")

    @classmethod
    def load_analysis(cls, doc_id: str) -> DocumentAnalysis | None:
        f = cls.get_doc_dir(doc_id) / "analysis.json"
        if f.exists():
            return DocumentAnalysis.model_validate_json(f.read_text(encoding="utf-8"))
        return None

    @classmethod
    def save_text_blocks(cls, doc_id: str, blocks: list[TextBlock]):
        f = cls.get_doc_dir(doc_id) / "text_blocks.json"
        data = [b.model_dump() for b in blocks]
        f.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load_text_blocks(cls, doc_id: str) -> list[TextBlock]:
        f = cls.get_doc_dir(doc_id) / "text_blocks.json"
        if f.exists():
            raw = json.loads(f.read_text(encoding="utf-8"))
            return [TextBlock.model_validate(b) for b in raw]
        return []

    @classmethod
    def save_hyperlinks(cls, doc_id: str, links: list[HyperlinkItem]):
        f = cls.get_doc_dir(doc_id) / "hyperlinks.json"
        data = [l.model_dump() for l in links]
        f.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load_hyperlinks(cls, doc_id: str) -> list[HyperlinkItem]:
        f = cls.get_doc_dir(doc_id) / "hyperlinks.json"
        if f.exists():
            raw = json.loads(f.read_text(encoding="utf-8"))
            return [HyperlinkItem.model_validate(l) for l in raw]
        return []

    @classmethod
    def save_assets(cls, doc_id: str, assets: list[VisualAsset]):
        f = cls.get_doc_dir(doc_id) / "assets_meta.json"
        data = [a.model_dump() for a in assets]
        f.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load_assets(cls, doc_id: str) -> list[VisualAsset]:
        f = cls.get_doc_dir(doc_id) / "assets_meta.json"
        if f.exists():
            raw = json.loads(f.read_text(encoding="utf-8"))
            return [VisualAsset.model_validate(a) for a in raw]
        return []

    @classmethod
    def save_validation_report(cls, doc_id: str, report: ValidationReport):
        f = cls.get_doc_dir(doc_id) / "validation_report.json"
        f.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    @classmethod
    def load_validation_report(cls, doc_id: str) -> ValidationReport | None:
        f = cls.get_doc_dir(doc_id) / "validation_report.json"
        if f.exists():
            return ValidationReport.model_validate_json(f.read_text(encoding="utf-8"))
        return None

    @classmethod
    def save_branding(cls, branding: BrandingSettings):
        f = settings.STORAGE_DIR / "branding.json"
        f.write_text(branding.model_dump_json(indent=2), encoding="utf-8")

    @classmethod
    def load_branding(cls) -> BrandingSettings:
        f = settings.STORAGE_DIR / "branding.json"
        if f.exists():
            try:
                return BrandingSettings.model_validate_json(f.read_text(encoding="utf-8"))
            except Exception:
                pass
        return BrandingSettings()
