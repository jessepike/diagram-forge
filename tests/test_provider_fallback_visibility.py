"""A provider substitution must be visible in the response payload.

Background: on 2026-08-07 a caller explicitly requested `provider="openai"`, the OpenAI
account returned HTTP 429 `credit_balance_exhausted`, and the server fell through to Gemini
and returned `{"success": true, "provider_used": "gemini"}` with no error field. The caller
had no way to tell from the response that the provider it asked for had failed. A fallback
that hides the substitution is worse than one that fails, because the caller believes it got
what it asked for — and anyone benchmarking two providers is silently handed one of them.

Every test here pairs the failure case with a positive control. A test that only asserts
"a warning appears when a provider fails" cannot distinguish a working check from one that
warns unconditionally.
"""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from diagram_forge.cost_tracker import CostTracker
from diagram_forge.models import BillingModel, GenerationResult
from diagram_forge.server import create_server


def _result(success: bool, error: str | None = None) -> GenerationResult:
    return GenerationResult(
        success=success,
        image_data=b"\x89PNG-stub" if success else None,
        error_message=error,
        cost_usd=0.01,
        billing_model=BillingModel.PER_IMAGE,
        tokens_used=None,
        model_used="stub",
    )


class _StubProviderFactory:
    """Stands in for `get_provider`, returning a canned result per provider name."""

    def __init__(self, failures: dict[str, GenerationResult]):
        self.failures = failures

    def __call__(self, name: str, api_key: str, model: str | None = None):
        outcome = self.failures.get(name, _result(True))

        class _Provider:
            async def generate(self, _config):
                return outcome

        return _Provider()


def _unwrap(raw):
    """FastMCP returns content blocks; normalize to the tool's dict payload."""
    if isinstance(raw, tuple):
        raw = raw[-1]
    if isinstance(raw, list) and raw and hasattr(raw[0], "text"):
        raw = json.loads(raw[0].text)
    return raw


async def _generate(failures: dict[str, GenerationResult], provider: str, tmp_path):
    """Run generate_diagram against stub providers and an isolated cost database.

    CostTracker is redirected at tmp_path. The generation path records every attempt,
    so without this a test run writes fabricated rows — successes, and costs that were
    never charged — into the real usage ledger at ~/.diagram-forge/usage.db. That
    happened once while this fix was being written; the rows had to be deleted by hand.
    """
    with patch("diagram_forge.server.CostTracker") as tracker_cls:
        tracker_cls.return_value = CostTracker(tmp_path / "usage.db")
        app = create_server()

    with patch("diagram_forge.server.get_provider", _StubProviderFactory(failures)):
        return _unwrap(
            await app.call_tool(
                "generate_diagram",
                {
                    "prompt": "a box",
                    "provider": provider,
                    "output_path": str(tmp_path / "out.png"),
                },
            )
        )


@pytest.mark.asyncio
async def test_no_warning_when_requested_provider_succeeds(tmp_path):
    """POSITIVE CONTROL: nothing fell back, so the response must stay quiet.

    Without this, a check that always warns would pass the test below.
    """
    response = await _generate({}, "openai", tmp_path)

    assert response["status"] == "success"
    assert response["provider_used"] == "openai"
    assert response["requested_provider"] == "openai"
    assert response.get("warning") is None
    assert response.get("fell_back_from") is None


@pytest.mark.asyncio
async def test_substitution_is_reported_with_the_underlying_error(tmp_path):
    """The real defect: requested provider fails, another succeeds, caller must be told."""
    response = await _generate(
        {"openai": _result(False, "Error code: 429 - credit_balance_exhausted")},
        "openai",
        tmp_path,
    )

    # The image was still produced, so the call is a success...
    assert response["status"] == "success"
    assert response["provider_used"] != "openai"

    # ...but the substitution is stated, not implied.
    assert response["requested_provider"] == "openai"
    assert "openai" in response["warning"]
    assert response["provider_used"] in response["warning"]

    # And the reason the requested provider failed survives into the payload, so the
    # caller can act on it without going to the server logs or the cost database.
    failed = [a for a in response["fell_back_from"] if a.get("provider") == "openai"]
    assert len(failed) == 1
    assert "credit_balance_exhausted" in failed[0]["error"]
