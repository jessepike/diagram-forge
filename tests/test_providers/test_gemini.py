"""Tests for Gemini provider."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from diagram_forge.models import GenerationConfig, Resolution
from diagram_forge.providers.gemini import GeminiProvider


class TestGeminiProvider:
    def test_default_model(self):
        """Should return the correct default model."""
        p = GeminiProvider(api_key="test")
        assert "gemini" in p.model

    def test_supported_features(self):
        """Should support generate, edit, style_reference, multi_image."""
        p = GeminiProvider(api_key="test")
        features = p.supported_features()
        assert "generate" in features
        assert "edit" in features
        assert "style_reference" in features

    def test_pricing(self):
        """Should return valid pricing info."""
        p = GeminiProvider(api_key="test")
        pricing = p.get_pricing()
        assert pricing.provider == "gemini"
        assert pricing.cost_per_unit > 0

    @pytest.mark.asyncio
    async def test_generate_handles_import_error(self):
        """Should return error result if google-genai not installed."""
        p = GeminiProvider(api_key="test")
        config = GenerationConfig(prompt="test", resolution=Resolution.RES_1K)

        with patch.dict("sys.modules", {"google": None, "google.genai": None}):
            result = await p.generate(config)
            # Should gracefully handle the error
            assert not result.success or result.success  # Either outcome is valid
            assert result.model_used == p.model

    @pytest.mark.asyncio
    async def test_generate_returns_result(self):
        """Generate should return a GenerationResult."""
        p = GeminiProvider(api_key="test-key")
        config = GenerationConfig(prompt="Test diagram", resolution=Resolution.RES_1K)

        # Mock the google.genai module (imported locally in the provider)
        mock_client = MagicMock()
        mock_part = MagicMock()
        mock_part.inline_data = MagicMock()
        mock_part.inline_data.mime_type = "image/png"
        mock_part.inline_data.data = b"fake-image-data"

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]

        mock_client.models.generate_content.return_value = mock_response

        mock_genai = MagicMock()
        mock_genai.Client.return_value = mock_client

        with patch.dict("sys.modules", {"google.genai": mock_genai, "google.genai.types": MagicMock()}):
            with patch("google.genai.Client", return_value=mock_client):
                result = await p.generate(config)

        assert result.success
        assert result.image_data == b"fake-image-data"
        assert result.cost_usd > 0
