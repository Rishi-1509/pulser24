"""
Health-check endpoint — confirms the API is running and reachable.
"""

from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Return service status and uptime metadata."""
    return {
        "status": "healthy",
        "service": "Pulse R24 Email Publishing Studio",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "engines": {
            "pdf_extraction": "not_initialized",
            "html_generation": "not_initialized",
            "image_processing": "not_initialized",
        },
    }
