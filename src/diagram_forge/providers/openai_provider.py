"""OpenAI image generation provider (GPT Image 2 / DALL-E)."""

from __future__ import annotations

import base64
import time

from diagram_forge.models import (
    BillingModel,
    GenerationConfig,
    GenerationResult,
    PricingInfo,
    ProviderHealth,
)
from diagram_forge.providers.base import BaseImageProvider


# Per-image cost in USD, keyed by (size, quality).
# Source: https://developers.openai.com/api/docs/guides/image-generation (2026-04-21).
_GPT_IMAGE_2_COSTS: dict[tuple[str, str], float] = {
    ("1024x1024", "low"): 0.006,
    ("1024x1024", "medium"): 0.053,
    ("1024x1024", "high"): 0.211,
    ("1536x1024", "low"): 0.005,
    ("1536x1024", "medium"): 0.041,
    ("1536x1024", "high"): 0.165,
    ("1024x1536", "low"): 0.005,
    ("1024x1536", "medium"): 0.041,
    ("1024x1536", "high"): 0.165,
}

_GPT_IMAGE_1_MINI_COSTS: dict[tuple[str, str], float] = {
    ("1024x1024", "low"): 0.005,
    ("1024x1024", "medium"): 0.011,
    ("1024x1024", "high"): 0.036,
    ("1536x1024", "low"): 0.006,
    ("1536x1024", "medium"): 0.015,
    ("1536x1024", "high"): 0.052,
    ("1024x1536", "low"): 0.006,
    ("1024x1536", "medium"): 0.015,
    ("1024x1536", "high"): 0.052,
}

# gpt-image-1.5 pre-tiered flat rates (legacy fallback).
_GPT_IMAGE_15_FLAT = {"1024x1024": 0.009, "1536x1024": 0.013, "1024x1536": 0.013}


class OpenAIProvider(BaseImageProvider):
    """Provider for OpenAI image generation (GPT Image 2 / DALL-E 3)."""

    def default_model(self) -> str:
        return "gpt-image-2-2026-04-21"

    def _resolve_size(self, config: GenerationConfig) -> str:
        """Map resolution + aspect ratio to OpenAI size string."""
        ar = config.aspect_ratio.value
        if ar == "16:9":
            return "1536x1024"
        elif ar == "9:16":
            return "1024x1536"
        elif ar == "1:1":
            return "1024x1024"
        elif ar == "4:3":
            return "1536x1024"
        return "1024x1024"

    async def generate(self, config: GenerationConfig) -> GenerationResult:
        # Route to edit when a reference image is provided — GPT's edit API
        # supports image input, letting it use the reference as a visual style guide.
        if config.style_reference_path and config.style_reference_path.exists():
            image_bytes = config.style_reference_path.read_bytes()
            return await self.edit(image_bytes, config)

        start = time.monotonic()
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key)
            size = self._resolve_size(config)
            quality = config.quality.value

            # Only pass quality to models that accept it (gpt-image-2, gpt-image-1-mini).
            # dall-e-3 uses a different quality vocabulary; gpt-image-1.5 ignored it.
            kwargs: dict = {
                "model": self.model,
                "prompt": config.prompt,
                "n": 1,
                "size": size,
            }
            if self._supports_quality():
                kwargs["quality"] = quality

            response = await client.images.generate(**kwargs)

            elapsed_ms = int((time.monotonic() - start) * 1000)

            if response.data and response.data[0].b64_json:
                image_data = base64.b64decode(response.data[0].b64_json)
                cost = self._estimate_cost(size, quality)
                return GenerationResult(
                    success=True,
                    image_data=image_data,
                    model_used=self.model,
                    cost_usd=cost,
                    billing_model=BillingModel.PER_IMAGE,
                    generation_time_ms=elapsed_ms,
                )

            return self._make_error_result("No image in OpenAI response", elapsed_ms)

        except Exception as e:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return self._make_error_result(str(e), elapsed_ms)

    def _supports_quality(self) -> bool:
        """True if model accepts low|medium|high|auto quality param."""
        return "image-2" in self.model or "image-1-mini" in self.model

    def _estimate_cost(self, size: str, quality: str = "auto") -> float:
        """Estimate cost based on model, size, and quality tier.

        Uses per-image cost tables from OpenAI docs (2026-04-21). For `auto`
        quality, estimates at `medium` tier — typical resolved tier for diagrams.
        Unknown size/model falls back to a conservative mid-range estimate.
        """
        # Normalize auto to medium for cost estimation.
        q = "medium" if quality == "auto" else quality

        if "image-2" in self.model:
            return _GPT_IMAGE_2_COSTS.get((size, q), 0.041)
        if "image-1-mini" in self.model:
            return _GPT_IMAGE_1_MINI_COSTS.get((size, q), 0.015)
        if "1.5" in self.model:
            # gpt-image-1.5 is flat-rate, no quality tiers.
            return _GPT_IMAGE_15_FLAT.get(size, 0.013)
        # Legacy gpt-image-1 fallback.
        return 0.011 if size == "1024x1024" else 0.016

    async def edit(self, input_image: bytes, config: GenerationConfig) -> GenerationResult:
        start = time.monotonic()
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key)
            size = self._resolve_size(config)
            quality = config.quality.value

            kwargs: dict = {
                "model": self.model,
                "image": input_image,
                "prompt": config.prompt,
                "n": 1,
                "size": size,
            }
            if self._supports_quality():
                kwargs["quality"] = quality

            response = await client.images.edit(**kwargs)

            elapsed_ms = int((time.monotonic() - start) * 1000)

            if response.data and response.data[0].b64_json:
                image_data = base64.b64decode(response.data[0].b64_json)
                cost = self._estimate_cost(size, quality)
                return GenerationResult(
                    success=True,
                    image_data=image_data,
                    model_used=self.model,
                    cost_usd=cost,
                    billing_model=BillingModel.PER_IMAGE,
                    generation_time_ms=elapsed_ms,
                )

            return self._make_error_result("No image in OpenAI edit response", elapsed_ms)

        except Exception as e:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return self._make_error_result(str(e), elapsed_ms)

    async def health_check(self) -> ProviderHealth:
        start = time.monotonic()
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key)
            _ = await client.models.list()
            elapsed = int((time.monotonic() - start) * 1000)
            return ProviderHealth(
                available=True,
                provider="openai",
                model=self.model,
                message="OpenAI API accessible",
                latency_ms=elapsed,
            )
        except Exception as e:
            elapsed = int((time.monotonic() - start) * 1000)
            return ProviderHealth(
                available=False,
                provider="openai",
                model=self.model,
                message=f"OpenAI API error: {e}",
                latency_ms=elapsed,
            )

    def get_pricing(self) -> PricingInfo:
        """Return representative pricing — medium quality at 1536x1024."""
        unit_cost = self._estimate_cost("1536x1024", "medium")
        return PricingInfo(
            provider="openai",
            model=self.model,
            billing_model=BillingModel.PER_IMAGE,
            cost_per_unit=unit_cost,
            unit_description=f"per image (1536x1024, medium, {self.model})",
        )

    def supported_features(self) -> set[str]:
        return {"generate", "edit"}
