from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global application settings."""

    APP_NAME: str = "Pulse R24 Email Publishing Studio"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Paths (relative to workspace root)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage"
    UPLOAD_DIR: Path = STORAGE_DIR / "uploads"
    EXTRACTED_DIR: Path = STORAGE_DIR / "extracted"
    GENERATED_DIR: Path = STORAGE_DIR / "generated"
    EXPORTS_DIR: Path = STORAGE_DIR / "exports"
    SAMPLE_DATA_DIR: Path = BASE_DIR / "sample-data"

    # Security
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: set[str] = {".pdf"}

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # OCR Fallback
    TESSERACT_CMD: str | None = None

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()

# Ensure directories exist
for folder in [settings.STORAGE_DIR, settings.UPLOAD_DIR, settings.EXTRACTED_DIR, settings.GENERATED_DIR, settings.EXPORTS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)
