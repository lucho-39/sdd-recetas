"""Tests for the image upload endpoint."""
from httpx import AsyncClient

from app.core.config import get_settings

# Minimal payload starting with the PNG signature (enough for signature sniffing).
PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000a49444154789c63600000020001e221bc330000000049454e44ae426082"
)


async def test_upload_image(client: AsyncClient, auth_headers: dict, tmp_path) -> None:
    settings = get_settings()
    original = settings.UPLOADS_DIR
    settings.UPLOADS_DIR = str(tmp_path)
    try:
        response = await client.post(
            "/api/v1/uploads",
            files={"file": ("test.png", PNG_BYTES, "image/png")},
            headers=auth_headers,
        )
    finally:
        settings.UPLOADS_DIR = original

    assert response.status_code == 201
    body = response.json()
    assert body["url"].startswith("/uploads/")
    assert body["url"].endswith(".png")
    assert (tmp_path / body["filename"]).exists()


async def test_upload_rejects_unsupported_type(
    client: AsyncClient, auth_headers: dict, tmp_path
) -> None:
    settings = get_settings()
    original = settings.UPLOADS_DIR
    settings.UPLOADS_DIR = str(tmp_path)
    try:
        response = await client.post(
            "/api/v1/uploads",
            files={"file": ("test.txt", b"hello", "text/plain")},
            headers=auth_headers,
        )
    finally:
        settings.UPLOADS_DIR = original

    assert response.status_code == 400


async def test_upload_rejects_fake_image(
    client: AsyncClient, auth_headers: dict, tmp_path
) -> None:
    settings = get_settings()
    original = settings.UPLOADS_DIR
    settings.UPLOADS_DIR = str(tmp_path)
    try:
        response = await client.post(
            "/api/v1/uploads",
            files={"file": ("evil.png", b"definitely not an image", "image/png")},
            headers=auth_headers,
        )
    finally:
        settings.UPLOADS_DIR = original

    assert response.status_code == 400


async def test_upload_requires_authentication(client: AsyncClient, tmp_path) -> None:
    response = await client.post(
        "/api/v1/uploads",
        files={"file": ("test.png", PNG_BYTES, "image/png")},
    )
    assert response.status_code == 401
