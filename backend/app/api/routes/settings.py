from fastapi import APIRouter
from app.models.schemas import BrandingSettings
from app.services.session_manager import SessionStore

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/branding", response_model=BrandingSettings)
async def get_branding():
    return SessionStore.load_branding()


@router.post("/branding", response_model=BrandingSettings)
async def update_branding(settings_data: BrandingSettings):
    SessionStore.save_branding(settings_data)
    return settings_data
