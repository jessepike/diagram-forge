"""POST /generate — diagram generation endpoint (mock for WUI-01)."""

from __future__ import annotations

import base64

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

# 1x1 transparent PNG (67 bytes) used as placeholder
_PLACEHOLDER_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4"
    "nGNgYPgPAAEDAQAIicLsAAAABJRU5ErkJggg=="
)


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
    """Generate a diagram (mock implementation — real wiring in WUI-03)."""
    if body.provider == "auto":
        raise HTTPException(status_code=400, detail="Provider 'auto' is not supported; choose 'gemini' or 'openai'")

    if len(body.content) > 50_000:
        raise HTTPException(status_code=400, detail="Content exceeds 50,000 character limit")

    # Mock response — WUI-03 will replace with real generation
    model = body.model or ("gemini-2.0-flash-preview-image-generation" if body.provider == "gemini" else "gpt-image-1")
    return GenerateResponse(
        image_base64=_PLACEHOLDER_PNG,
        provider=body.provider,
        model=model,
        cost_usd=0.0,
    )
