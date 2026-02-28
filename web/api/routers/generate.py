"""POST /generate — diagram generation endpoint."""

from __future__ import annotations

import asyncio
import base64

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from diagram_forge.models import GenerationConfig
from diagram_forge.providers import get_provider
from diagram_forge.template_engine import build_prompt

router = APIRouter()

_MAX_IMAGE_BYTES = 3_145_728  # 3 MB cap


class GenerateRequest(BaseModel):
    template_id: str
    content: str = Field(max_length=50_000)
    provider: str
    api_key: str
    model: str | None = None


class GenerateResponse(BaseModel):
    image_base64: str
    provider: str
    model: str
    cost_usd: float


@router.post("/generate", response_model=GenerateResponse)
async def generate_diagram(body: GenerateRequest) -> GenerateResponse:
    """Generate a diagram via a diagram-forge provider."""
    if body.provider == "auto":
        raise HTTPException(
            status_code=400,
            detail="Provider 'auto' is not supported; choose 'gemini', 'openai', or 'replicate'",
        )

    # Build the prompt from template + user content
    rendered_prompt = build_prompt(body.template_id, body.content)

    # Instantiate provider
    try:
        provider_kwargs: dict = {}
        if body.model:
            provider_kwargs["model"] = body.model
        provider = get_provider(body.provider, body.api_key, **provider_kwargs)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Generate with timeout
    gen_config = GenerationConfig(prompt=rendered_prompt)
    try:
        result = await asyncio.wait_for(provider.generate(gen_config), timeout=60)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Provider generation timed out (60s limit)")
    except Exception as exc:
        # Map auth-like errors
        msg = str(exc).lower()
        if "unauthorized" in msg or "invalid api key" in msg or "401" in msg:
            raise HTTPException(status_code=401, detail=f"Provider auth error: {exc}") from exc
        if "forbidden" in msg or "403" in msg:
            raise HTTPException(status_code=403, detail=f"Provider access denied: {exc}") from exc
        raise HTTPException(status_code=502, detail=f"Provider error: {exc}") from exc

    # Check generation success
    if not result.success:
        raise HTTPException(status_code=502, detail=f"Generation failed: {result.error_message}")

    if result.image_data is None:
        raise HTTPException(status_code=502, detail="Generation succeeded but returned no image data")

    # Enforce size cap
    if len(result.image_data) > _MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Generated image exceeds 3 MB limit ({len(result.image_data):,} bytes)",
        )

    image_b64 = base64.b64encode(result.image_data).decode()

    return GenerateResponse(
        image_base64=image_b64,
        provider=body.provider,
        model=result.model_used,
        cost_usd=result.cost_usd,
    )
