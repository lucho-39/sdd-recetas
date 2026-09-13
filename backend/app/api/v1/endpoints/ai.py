"""
AI recipe generation (v2, config-gated).

Calls an OpenAI-compatible chat completions API. If ``AI_API_KEY`` is not set
the endpoint returns 503 (the feature is considered disabled).
"""
import json

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.security import get_current_active_user

router = APIRouter()

_SYSTEM_PROMPT = (
    "Sos un chef profesional. A partir de los ingredientes y preferencias del "
    "usuario, devolvés SIEMPRE un objeto JSON con esta forma exacta: "
    '{"title": str, "description": str, "difficulty": "easy"|"medium"|"hard", '
    '"prep_time_minutes": int, "cook_time_minutes": int, "servings": int, '
    '"instructions": str, "tags": [str], '
    '"ingredients": [{"name": str, "amount": number, "unit": str}]}. '
    "No incluyas texto fuera del JSON."
)


class GenerateRecipeRequest(BaseModel):
    ingredients: str = Field(..., min_length=3, max_length=1000)
    preferences: str | None = Field(None, max_length=500)
    servings: int | None = Field(None, ge=1, le=20)


@router.post("/generate", summary="Generate a recipe draft with AI")
async def generate_recipe(
    data: GenerateRecipeRequest,
    current_user=Depends(get_current_active_user),
):
    settings = get_settings()
    if not settings.AI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI recipe generation is not configured",
        )

    prompt = f"Ingredientes disponibles: {data.ingredients}"
    if data.preferences:
        prompt += f"\nPreferencias: {data.preferences}"
    if data.servings:
        prompt += f"\nPorciones deseadas: {data.servings}"

    payload = {
        "model": settings.AI_MODEL,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{settings.AI_BASE_URL.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {settings.AI_API_KEY}"},
                json=payload,
            )
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="AI provider is unreachable"
        )

    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI provider error")

    try:
        content = response.json()["choices"][0]["message"]["content"]
        draft = json.loads(content)
    except (KeyError, IndexError, json.JSONDecodeError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="AI returned an invalid response"
        )

    return {"draft": draft}
