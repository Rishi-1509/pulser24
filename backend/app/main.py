"""
Pulse R24 Email Publishing Studio - FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import assets, export, generate, health, hyperlinks, pdf, settings as settings_routes


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Convert Pulse R24 PDF newsletters into responsive, email-compatible HTML.",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Routers
    app.include_router(health.router, prefix="/api")
    app.include_router(pdf.router, prefix="/api")
    app.include_router(hyperlinks.router, prefix="/api")
    app.include_router(assets.router)
    app.include_router(generate.router, prefix="/api")
    app.include_router(export.router, prefix="/api")
    app.include_router(settings_routes.router, prefix="/api")

    # Import validation router
    from app.api.routes import validation
    app.include_router(validation.router, prefix="/api")

    return app


app = create_app()
