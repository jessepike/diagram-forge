"""Replicate image generation provider (Flux models)."""

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


class ReplicateProvider(BaseImageProvider):
    """Provider for Replicate-hosted image generation models (Flux)."""

    def default_model(self) -> str:
        return "black-forest-labs/flux-schnell"

    def _resolve_dimensions(self, config: GenerationConfig) -> dict:
        """Map resolution + aspect ratio to width/height."""
        base = {"1K": 1024, "2K": 1536, "4K": 2048}.get(config.resolution.value, 1024)
        ar = config.aspect_ratio.value
        if ar == "16:9":
            return {"width": base, "height": int(base * 9 / 16)}
        elif ar == "9:16":
            return {"width": int(base * 9 / 16), "height": base}
        elif ar == "4:3":
            return {"width": base, "height": int(base * 3 / 4)}
        return {"width": base, "height": base}

    async def generate(self, config: GenerationConfig) -> GenerationResult:
        start = time.monotonic()
        try:
            import httpx
            import replicate

            client = replicate.Client(api_token=self.api_key)
            dims = self._resolve_dimensions(config)

            output = client.run(
                self.model,
                input={
                    "prompt": config.prompt,
                    "width": dims["width"],
                    "height": dims["height"],
                    "num_outputs": 1,
                },
            )

            elapsed_ms = int((time.monotonic() - start) * 1000)

            # Output is typically a list of URLs or FileOutput objects
            if output:
                image_url = output[0] if isinstance(output, list) else output
                url = str(image_url)

                # Download the image
                async with httpx.AsyncClient() as http:
                    resp = await http.get(url)
                    resp.raise_for_status()
                    image_data = resp.content

                # Estimate cost: ~2s generation at $0.003/s
                est_seconds = elapsed_ms / 1000
                cost = round(est_seconds * 0.003, 6)

                return GenerationResult(
                    success=True,
                    image_data=image_data,
                    model_used=self.model,
                    cost_usd=cost,
                    billing_model=BillingModel.PER_SECOND,
                    generation_time_ms=elapsed_ms,
                )

            return self._make_error_result("No output from Replicate", elapsed_ms)

        except Exception as e:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return self._make_error_result(str(e), elapsed_ms)

    async def edit(self, input_image: bytes, config: GenerationConfig) -> GenerationResult:
        """Replicate Flux doesn't natively support image editing.

        Falls back to img2img if available, otherwise returns error.
        """
        start = time.monotonic()
        try:
            import base64

            import httpx
            import replicate

            client = replicate.Client(api_token=self.api_key)
            dims = self._resolve_dimensions(config)

            # Encode input image as data URI for Replicate
            b64 = base64.b64encode(input_image).decode()
            data_uri = f"data:image/png;base64,{b64}"

            output = client.run(
                self.model,
                input={
                    "prompt": config.prompt,
                    "image": data_uri,
                    "width": dims["width"],
                    "height": dims["height"],
                    "num_outputs": 1,
                },
            )

            elapsed_ms = int((time.monotonic() - start) * 1000)

            if output:
                image_url = output[0] if isinstance(output, list) else output
                url = str(image_url)

                async with httpx.AsyncClient() as http:
                    resp = await http.get(url)
                    resp.raise_for_status()
                    image_data = resp.content

                est_seconds = elapsed_ms / 1000
                cost = round(est_seconds * 0.003, 6)

                return GenerationResult(
                    success=True,
                    image_data=image_data,
                    model_used=self.model,
                    cost_usd=cost,
                    billing_model=BillingModel.PER_SECOND,
                    generation_time_ms=elapsed_ms,
                )

            return self._make_error_result("No output from Replicate edit", elapsed_ms)

        except Exception as e:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return self._make_error_result(str(e), elapsed_ms)

    async def health_check(self) -> ProviderHealth:
        start = time.monotonic()
        try:
            import replicate

            client = replicate.Client(api_token=self.api_key)
            _ = client.models.get(self.model)
            elapsed = int((time.monotonic() - start) * 1000)
            return ProviderHealth(
                available=True,
                provider="replicate",
                model=self.model,
                message="Replicate API accessible",
                latency_ms=elapsed,
            )
        except Exception as e:
            elapsed = int((time.monotonic() - start) * 1000)
            return ProviderHealth(
                available=False,
                provider="replicate",
                model=self.model,
                message=f"Replicate API error: {e}",
                latency_ms=elapsed,
            )

    def get_pricing(self) -> PricingInfo:
        return PricingInfo(
            provider="replicate",
            model=self.model,
            billing_model=BillingModel.PER_SECOND,
            cost_per_unit=0.003,
            unit_description="per second of GPU time (~2s per image)",
        )

    def supported_features(self) -> set[str]:
        return {"generate"}
