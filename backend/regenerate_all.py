import json
from pathlib import Path
from app.models.schemas import TextBlock, HyperlinkItem, VisualAsset, BrandingSettings
from app.services.html_generation.generator import EmailGeneratorService

docs = ["17da418c", "ref_359"]

for doc_id in docs:
    ext_dir = Path(f"storage/extracted/{doc_id}")
    gen_dir = Path(f"storage/generated/{doc_id}")
    gen_dir.mkdir(parents=True, exist_ok=True)
    
    if not ext_dir.exists():
        continue

    with open(ext_dir / "text_blocks.json", encoding="utf-8") as f:
        blocks_data = json.load(f)
        blocks = [TextBlock(**b) for b in blocks_data]

    with open(ext_dir / "hyperlinks.json", encoding="utf-8") as f:
        links_data = json.load(f)
        links = [HyperlinkItem(**l) for l in links_data]

    assets = []
    if (ext_dir / "assets_meta.json").exists():
        with open(ext_dir / "assets_meta.json", encoding="utf-8") as f:
            assets_data = json.load(f)
            assets = [VisualAsset(**a) for a in assets_data]

    page_images = sorted([p.name for p in ext_dir.glob("page_*.png")])

    pdf_path = None
    upload_matches = list(Path("storage/uploads").glob(f"{doc_id}*.pdf")) + list(Path("backend/uploads").glob(f"{doc_id}*.pdf"))
    if upload_matches:
        pdf_path = str(upload_matches[0])

    svc = EmailGeneratorService(
        doc_id=doc_id,
        text_blocks=blocks,
        hyperlinks=links,
        assets=assets,
        page_images=page_images,
        branding=BrandingSettings(),
        pdf_path=pdf_path
    )

    # Mode reconstructed
    html_rec, txt_rec = svc.generate_reconstructed_mode()
    with open(gen_dir / "email.html", "w", encoding="utf-8") as f:
        f.write(html_rec)
    with open(gen_dir / "email_reconstructed.html", "w", encoding="utf-8") as f:
        f.write(html_rec)
    with open(gen_dir / "email.txt", "w", encoding="utf-8") as f:
        f.write(txt_rec)

    # Mode faithful
    html_fth, _ = svc.generate_faithful_mode()
    with open(gen_dir / "email_faithful.html", "w", encoding="utf-8") as f:
        f.write(html_fth)

    print(f"Successfully generated HTML for {doc_id} (Length: {len(html_rec)} chars, Links: {len(links)})")
