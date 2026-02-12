"""Provider registry and factory for image generation providers."""

from diagram_forge.providers.base import BaseImageProvider
from diagram_forge.providers.gemini import GeminiProvider
from diagram_forge.providers.openai_provider import OpenAIProvider
from diagram_forge.providers.replicate_provider import ReplicateProvider

PROVIDER_MAP: dict[str, type[BaseImageProvider]] = {
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
    "replicate": ReplicateProvider,
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
    "ReplicateProvider",
    "PROVIDER_MAP",
    "get_provider",
]
