"""Abstract base class for image generation providers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from diagram_forge.models import (
    BillingModel,
    GenerationConfig,
    GenerationResult,
    PricingInfo,
    ProviderHealth,
)


class BaseImageProvider(ABC):
    """Abstract base for all image generation providers.

    Each provider implements generate, edit, health_check, pricing, and feature reporting.
    """

    def __init__(self, api_key: str, model: str | None = None, **kwargs):
        self.api_key = api_key
        self.model = model or self.default_model()
        self.extra = kwargs

    @abstractmethod
    def default_model(self) -> str:
        """Return the default model identifier for this provider."""
        ...

    @abstractmethod
    async def generate(self, config: GenerationConfig) -> GenerationResult:
        """Generate an image from a text prompt."""
        ...

    @abstractmethod
    async def edit(self, input_image: bytes, config: GenerationConfig) -> GenerationResult:
        """Edit an existing image based on a prompt."""
        ...

    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        """Verify API connectivity and readiness."""
        ...

    @abstractmethod
    def get_pricing(self) -> PricingInfo:
        """Return pricing information for this provider."""
        ...

    @abstractmethod
    def supported_features(self) -> set[str]:
        """Return set of supported feature strings.

        Common features: "generate", "edit", "multi_image", "4K", "style_reference"
        """
        ...

    def _make_error_result(self, error: str, time_ms: int = 0) -> GenerationResult:
        """Helper to create a failed GenerationResult."""
        return GenerationResult(
            success=False,
            error_message=error,
            model_used=self.model,
            generation_time_ms=time_ms,
            billing_model=BillingModel.PER_IMAGE,
        )
