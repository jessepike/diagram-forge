"""Shared test fixtures and mock providers."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from diagram_forge.models import (
    BillingModel,
    GenerationConfig,
    GenerationResult,
    ProviderHealth,
    PricingInfo,
    Resolution,
)
from diagram_forge.providers.base import BaseImageProvider


class MockProvider(BaseImageProvider):
    """Mock provider for testing that returns predictable results."""

    def default_model(self) -> str:
        return "mock-model-v1"

    async def generate(self, config: GenerationConfig) -> GenerationResult:
        # Return a tiny valid PNG
        return GenerationResult(
            success=True,
            image_data=TINY_PNG,
            model_used=self.model,
            cost_usd=0.01,
            billing_model=BillingModel.PER_IMAGE,
            generation_time_ms=100,
        )

    async def edit(self, input_image: bytes, config: GenerationConfig) -> GenerationResult:
        return GenerationResult(
            success=True,
            image_data=TINY_PNG,
            model_used=self.model,
            cost_usd=0.01,
            billing_model=BillingModel.PER_IMAGE,
            generation_time_ms=50,
        )

    async def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            available=True,
            provider="mock",
            model=self.model,
            message="Mock provider always healthy",
            latency_ms=1,
        )

    def get_pricing(self) -> PricingInfo:
        return PricingInfo(
            provider="mock",
            model=self.model,
            billing_model=BillingModel.PER_IMAGE,
            cost_per_unit=0.01,
            unit_description="per image (mock)",
        )

    def supported_features(self) -> set[str]:
        return {"generate", "edit", "style_reference"}


class FailingProvider(BaseImageProvider):
    """Mock provider that always fails."""

    def default_model(self) -> str:
        return "fail-model-v1"

    async def generate(self, config: GenerationConfig) -> GenerationResult:
        return GenerationResult(
            success=False,
            error_message="Simulated failure",
            model_used=self.model,
            billing_model=BillingModel.PER_IMAGE,
        )

    async def edit(self, input_image: bytes, config: GenerationConfig) -> GenerationResult:
        return GenerationResult(
            success=False,
            error_message="Simulated edit failure",
            model_used=self.model,
            billing_model=BillingModel.PER_IMAGE,
        )

    async def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            available=False,
            provider="failing",
            model=self.model,
            message="Always fails",
        )

    def get_pricing(self) -> PricingInfo:
        return PricingInfo(
            provider="failing",
            model=self.model,
            billing_model=BillingModel.PER_IMAGE,
            cost_per_unit=0.0,
            unit_description="free (always fails)",
        )

    def supported_features(self) -> set[str]:
        return {"generate"}


# Minimal valid 1x1 white PNG
TINY_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
    b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
    b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest.fixture
def mock_provider():
    """Create a mock provider instance."""
    return MockProvider(api_key="test-key")


@pytest.fixture
def failing_provider():
    """Create a failing provider instance."""
    return FailingProvider(api_key="test-key")


@pytest.fixture
def tmp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def generation_config():
    """Create a default generation config."""
    return GenerationConfig(
        prompt="Test diagram: a simple box with an arrow",
        resolution=Resolution.RES_1K,
    )


@pytest.fixture
def tiny_png():
    """Return a minimal valid PNG image."""
    return TINY_PNG
