"""OpenAI image generation provider (GPT Image 1.5 / DALL-E)."""

from __future__ import annotations

import base64
import time
from typing import Literal

from diagram_forge.models import (
    BillingModel,
    GenerationConfig,
    GenerationResult,
    PricingInfo,
    ProviderHealth,
)
from diagram_forge.providers.base import BaseImageProvider


class OpenAIProvider(BaseImageProvider):
    """Provider for OpenAI image generation (GPT Image 1.5 / DALL-E 3)."""

    def default_model(self) -> str:
        return "gpt-image-1.5"

    def _resolve_size(
        self, config: GenerationConfig
    ) -> Literal["1024x1024", "1536x1024", "1024x1536"]:
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
        start = time.monotonic()
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key)
            size = self._resolve_size(config)

            response = await client.images.generate(
                model=self.model,
                prompt=config.prompt,
                n=1,
                size=size,
                response_format="b64_json",
            )

            elapsed_ms = int((time.monotonic() - start) * 1000)

            if response.data and response.data[0].b64_json:
                image_data = base64.b64decode(response.data[0].b64_json)
                # Estimate cost based on size
                cost = self._estimate_cost(size)
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

    def _estimate_cost(self, size: str) -> float:
        """Estimate cost based on model and size."""
        if "1.5" in self.model:
            return 0.009 if size == "1024x1024" else 0.013
        return 0.011 if size == "1024x1024" else 0.016

    async def edit(self, input_image: bytes, config: GenerationConfig) -> GenerationResult:
        start = time.monotonic()
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key)
            size = self._resolve_size(config)

            response = await client.images.edit(
                model=self.model,
                image=input_image,
                prompt=config.prompt,
                n=1,
                size=size,
                response_format="b64_json",
            )

            elapsed_ms = int((time.monotonic() - start) * 1000)

            if response.data and response.data[0].b64_json:
                image_data = base64.b64decode(response.data[0].b64_json)
                cost = self._estimate_cost(size)
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
        return PricingInfo(
            provider="openai",
            model=self.model,
            billing_model=BillingModel.PER_IMAGE,
            cost_per_unit=0.013 if "1.5" in self.model else 0.016,
            unit_description=f"per image (1536x1024, {self.model})",
        )

    def supported_features(self) -> set[str]:
        return {"generate", "edit"}
