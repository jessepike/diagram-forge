"""Google Gemini image generation provider."""

from __future__ import annotations

import time

from diagram_forge.models import (
    BillingModel,
    GenerationConfig,
    GenerationResult,
    PricingInfo,
    ProviderHealth,
)
from diagram_forge.providers.base import BaseImageProvider


class GeminiProvider(BaseImageProvider):
    """Provider for Google Gemini image generation."""

    def default_model(self) -> str:
        return "gemini-2.5-flash-image"

    async def generate(self, config: GenerationConfig) -> GenerationResult:
        start = time.monotonic()
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)

            # Build generation config
            gen_config = types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
                temperature=config.temperature,
            )

            # Build prompt parts
            contents: list = [config.prompt]

            # Add style reference if provided
            if config.style_reference_path and config.style_reference_path.exists():
                ref_bytes = config.style_reference_path.read_bytes()
                suffix = config.style_reference_path.suffix.lower()
                mime = {
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".webp": "image/webp",
                }.get(suffix, "image/png")
                contents.insert(0, types.Part.from_bytes(data=ref_bytes, mime_type=mime))

            # Add reference images
            for ref_path in config.reference_images:
                if ref_path.exists():
                    ref_bytes = ref_path.read_bytes()
                    suffix = ref_path.suffix.lower()
                    mime = {
                        ".png": "image/png",
                        ".jpg": "image/jpeg",
                        ".jpeg": "image/jpeg",
                        ".webp": "image/webp",
                    }.get(suffix, "image/png")
                    contents.insert(0, types.Part.from_bytes(data=ref_bytes, mime_type=mime))

            response = client.models.generate_content(
                model=self.model,
                contents=contents,
                config=gen_config,
            )

            elapsed_ms = int((time.monotonic() - start) * 1000)

            # Extract image from response
            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                        return GenerationResult(
                            success=True,
                            image_data=part.inline_data.data,
                            model_used=self.model,
                            cost_usd=0.039,
                            billing_model=BillingModel.PER_IMAGE,
                            generation_time_ms=elapsed_ms,
                        )

            return self._make_error_result(
                "No image in Gemini response", elapsed_ms
            )

        except Exception as e:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return self._make_error_result(str(e), elapsed_ms)

    async def edit(self, input_image: bytes, config: GenerationConfig) -> GenerationResult:
        start = time.monotonic()
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)

            gen_config = types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
                temperature=config.temperature,
            )

            # Build contents with input image + edit prompt
            contents = [
                types.Part.from_bytes(data=input_image, mime_type="image/png"),
                config.prompt,
            ]

            # Add reference images
            for ref_path in config.reference_images:
                if ref_path.exists():
                    ref_bytes = ref_path.read_bytes()
                    suffix = ref_path.suffix.lower()
                    mime = {
                        ".png": "image/png",
                        ".jpg": "image/jpeg",
                        ".jpeg": "image/jpeg",
                        ".webp": "image/webp",
                    }.get(suffix, "image/png")
                    contents.insert(0, types.Part.from_bytes(data=ref_bytes, mime_type=mime))

            response = client.models.generate_content(
                model=self.model,
                contents=contents,
                config=gen_config,
            )

            elapsed_ms = int((time.monotonic() - start) * 1000)

            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                        return GenerationResult(
                            success=True,
                            image_data=part.inline_data.data,
                            model_used=self.model,
                            cost_usd=0.039,
                            billing_model=BillingModel.PER_IMAGE,
                            generation_time_ms=elapsed_ms,
                        )

            return self._make_error_result("No image in Gemini edit response", elapsed_ms)

        except Exception as e:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return self._make_error_result(str(e), elapsed_ms)

    async def health_check(self) -> ProviderHealth:
        start = time.monotonic()
        try:
            from google import genai

            client = genai.Client(api_key=self.api_key)
            # Simple model list check
            models = client.models.list()
            _ = next(iter(models), None)
            elapsed = int((time.monotonic() - start) * 1000)
            return ProviderHealth(
                available=True,
                provider="gemini",
                model=self.model,
                message="Gemini API accessible",
                latency_ms=elapsed,
            )
        except Exception as e:
            elapsed = int((time.monotonic() - start) * 1000)
            return ProviderHealth(
                available=False,
                provider="gemini",
                model=self.model,
                message=f"Gemini API error: {e}",
                latency_ms=elapsed,
            )

    def get_pricing(self) -> PricingInfo:
        return PricingInfo(
            provider="gemini",
            model=self.model,
            billing_model=BillingModel.PER_IMAGE,
            cost_per_unit=0.039,
            unit_description="per image generation",
        )

    def supported_features(self) -> set[str]:
        return {"generate", "edit", "style_reference", "multi_image"}
