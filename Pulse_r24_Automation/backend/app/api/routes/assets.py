from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.core.config import settings
from app.models.schemas import VisualAsset
from app.services.session_manager import SessionStore

router = APIRouter(tags=["assets"])


@router.get("/api/assets/{doc_id}", response_model=list[VisualAsset])
async def list_assets(doc_id: str):
    assets = SessionStore.load_assets(doc_id)
    return assets


@router.get("/api/assets/{doc_id}/{filename}")
async def get_asset_file(doc_id: str, filename: str):
    file_path = settings.EXTRACTED_DIR / doc_id / "assets" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Asset not found.")
    
    content_type = "image/png"
    if filename.endswith(".jpg") or filename.endswith(".jpeg"):
        content_type = "image/jpeg"
    elif filename.endswith(".svg"):
        content_type = "image/svg+xml"

    return FileResponse(file_path, media_type=content_type)


@router.get("/api/pages/{doc_id}/{filename}")
async def get_page_file(doc_id: str, filename: str):
    file_path = settings.EXTRACTED_DIR / doc_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Page render not found.")
    return FileResponse(file_path, media_type="image/png")
