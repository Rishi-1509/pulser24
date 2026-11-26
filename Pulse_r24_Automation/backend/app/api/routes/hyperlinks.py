from fastapi import APIRouter, HTTPException, Response
from app.models.schemas import HyperlinkItem, HyperlinkUpdateRequest
from app.services.hyperlink_extraction.extractor import HyperlinkExtractor
from app.services.session_manager import SessionStore

router = APIRouter(prefix="/hyperlinks", tags=["hyperlinks"])


@router.get("/{doc_id}", response_model=list[HyperlinkItem])
async def get_hyperlinks(doc_id: str):
    """Retrieve all extracted hyperlinks for a given document."""
    links = SessionStore.load_hyperlinks(doc_id)
    if not links:
        raise HTTPException(status_code=404, detail="No hyperlinks found for this document.")
    return links


@router.put("/{doc_id}/{link_id}", response_model=HyperlinkItem)
async def update_hyperlink(doc_id: str, link_id: str, update: HyperlinkUpdateRequest):
    """Edit or correct a hyperlink mapping association or visible text."""
    links = SessionStore.load_hyperlinks(doc_id)
    target = next((l for l in links if l.id == link_id), None)
    if not target:
        raise HTTPException(status_code=404, detail=f"Hyperlink {link_id} not found.")

    if update.visible_text is not None:
        target.visible_text = update.visible_text
    if update.url is not None:
        target.url = update.url
    if update.mapping_status is not None:
        target.mapping_status = update.mapping_status
    else:
        target.mapping_status = "manual"

    SessionStore.save_hyperlinks(doc_id, links)
    return target


@router.post("/{doc_id}", response_model=HyperlinkItem)
async def add_hyperlink(doc_id: str, item: HyperlinkItem):
    """Manually add a missing hyperlink."""
    links = SessionStore.load_hyperlinks(doc_id)
    links.append(item)
    SessionStore.save_hyperlinks(doc_id, links)
    return item


@router.get("/{doc_id}/export/json")
async def export_json(doc_id: str):
    links = SessionStore.load_hyperlinks(doc_id)
    if not links:
        raise HTTPException(status_code=404, detail="No hyperlinks found.")
    content = HyperlinkExtractor.export_to_json(links)
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=pulse_{doc_id}_hyperlinks.json"},
    )


@router.get("/{doc_id}/export/csv")
async def export_csv(doc_id: str):
    links = SessionStore.load_hyperlinks(doc_id)
    if not links:
        raise HTTPException(status_code=404, detail="No hyperlinks found.")
    content = HyperlinkExtractor.export_to_csv(links)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=pulse_{doc_id}_hyperlinks.csv"},
    )
