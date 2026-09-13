"""
Image upload endpoint (local disk).

Files are stored under ``settings.UPLOADS_DIR`` and served statically at
``/uploads``. The client stores the returned relative URL in
``recipe.image_url``.
"""
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.config import get_settings
from app.core.security import get_current_active_user

router = APIRouter()

CONTENT_TYPE_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def _is_supported_image(data: bytes) -> bool:
    """Validate the actual file signature (client content_type is spoofable)."""
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    if data.startswith(b"\xff\xd8\xff"):
        return True
    if data.startswith((b"GIF87a", b"GIF89a")):
        return True
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return True
    return False


@router.post("", status_code=status.HTTP_201_CREATED, summary="Upload an image")
async def upload_image(
    file: UploadFile = File(...),
    current_user = Depends(get_current_active_user),
):
    """Upload a recipe image and return its public URL."""
    settings = get_settings()

    if file.content_type not in CONTENT_TYPE_EXT:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    data = await file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail="File too large")
    if not data or not _is_supported_image(data):
        raise HTTPException(status_code=400, detail="Invalid image file")

    directory = Path(settings.UPLOADS_DIR)
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{CONTENT_TYPE_EXT[file.content_type]}"
    (directory / filename).write_bytes(data)

    return {"url": f"/uploads/{filename}", "filename": filename, "size": len(data)}
