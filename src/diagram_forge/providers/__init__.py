"""Provider registry and factory for image generation providers."""

from diagram_forge.providers.base import BaseImageProvider
from diagram_forge.providers.gemini import GeminiProvider
from diagram_forge.providers.openai_provider import OpenAIProvider

PROVIDER_MAP: dict[str, type[BaseImageProvider]] = {
    "gemini": GeminiProvider,
    "gemini_flash": GeminiProvider,        # legacy alias
    "gemini_flash_31": GeminiProvider,     # gemini-3.1-flash-image (current default)
    "gemini_flash_25": GeminiProvider,     # gemini-2.5-flash-image (deprecated, shut down Jan 2026)
    "openai": OpenAIProvider,              # default: gpt-image-2-2026-04-21
    "openai_mini": OpenAIProvider,         # gpt-image-1-mini (cheap tier, opt-in)
}


def get_provider(provider_name: str, api_key: str, **kwargs) -> BaseImageProvider:
    """Instantiate a provider by name."""
    provider_cls = PROVIDER_MAP.get(provider_name)
    if not provider_cls:
        raise ValueError(f"Unknown provider: {provider_name}. Available: {list(PROVIDER_MAP)}")
    return provider_cls(api_key=api_key, **kwargs)


__all__ = [
    "BaseImageProvider",
    "GeminiProvider",
    "OpenAIProvider",
    "PROVIDER_MAP",
    "get_provider",
]
