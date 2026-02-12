"""FastMCP server with all diagram generation tools."""

from __future__ import annotations

import time
from dataclasses import asdict
from pathlib import Path
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from diagram_forge.config import ensure_directories, load_config, resolve_api_key
from diagram_forge.cost_tracker import CostTracker
from diagram_forge.models import (
    AspectRatio,
    DiagramType,
    GenerationConfig,
    GenerationRecord,
    Resolution,
)
from diagram_forge.providers import PROVIDER_MAP, get_provider
from diagram_forge.style_manager import StyleManager
from diagram_forge.template_engine import build_prompt, load_all_templates


def _serialize(value: Any) -> Any:
    """Convert Pydantic models, dataclasses, UUIDs to JSON-serializable types."""
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if hasattr(value, "__dataclass_fields__"):
        d = asdict(value)
        # Remove bytes fields
        d.pop("image_data", None)
        return d
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, set):
        return sorted(value)
    return value


def create_server(config_path: str | None = None) -> Any:
    """Create and configure the Diagram Forge MCP server."""
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception as exc:
        raise RuntimeError(
            "MCP dependency is unavailable. Install with: pip install 'diagram-forge[dev]'"
        ) from exc

    # Load configuration
    config = load_config(config_path)
    ensure_directories(config)

    # Initialize components
    cost_tracker = CostTracker(config.database_path)
    style_manager = StyleManager(config.styles_directory)

    # Create FastMCP instance
    app = FastMCP("diagram-forge")

    def _run_tool(func, *args, _tool_name: str = "unknown", **kwargs):
        """Wrapper for timing and error handling."""
        start = time.monotonic()
        try:
            result = func(*args, **kwargs)
            return _serialize(result)
        except Exception as e:
            elapsed = int((time.monotonic() - start) * 1000)
            return {
                "status": "error",
                "error": str(e),
                "tool": _tool_name,
                "elapsed_ms": elapsed,
            }

    async def _run_tool_async(func, *args, _tool_name: str = "unknown", **kwargs):
        """Async wrapper for timing and error handling."""
        start = time.monotonic()
        try:
            result = await func(*args, **kwargs)
            return _serialize(result)
        except Exception as e:
            elapsed = int((time.monotonic() - start) * 1000)
            return {
                "status": "error",
                "error": str(e),
                "tool": _tool_name,
                "elapsed_ms": elapsed,
            }

    # --- Tool: generate_diagram ---

    @app.tool()
    async def generate_diagram(
        prompt: str,
        diagram_type: str = "generic",
        provider: str = "gemini",
        resolution: str = "2K",
        aspect_ratio: str = "16:9",
        style_reference: str | None = None,
        output_path: str | None = None,
        temperature: float = 1.0,
    ) -> dict:
        """Generate an architecture diagram from a text prompt.

        Args:
            prompt: Description of what to generate
            diagram_type: Type of diagram (architecture|data_flow|component|sequence|integration|infographic|generic)
            provider: Image generation provider (gemini|openai|replicate)
            resolution: Output resolution (1K|2K|4K)
            aspect_ratio: Output aspect ratio (16:9|1:1|9:16|4:3)
            style_reference: Style name or path to reference image
            output_path: Where to save the image (auto-generated if not provided)
            temperature: Generation creativity (0.0 to 2.0)
        """
        start = time.monotonic()

        # Resolve provider
        provider_config = config.providers.get(provider)
        if not provider_config:
            return {"status": "error", "error": f"Provider '{provider}' not configured"}

        api_key = resolve_api_key(provider_config)
        if not api_key:
            return {
                "status": "error",
                "error": f"No API key for provider '{provider}'. "
                f"Set {provider_config.api_key_env} environment variable.",
            }

        # Build the full prompt from template + user prompt
        full_prompt = build_prompt(
            diagram_type=diagram_type,
            user_prompt=prompt,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
        )

        # Resolve style reference
        style_path = None
        if style_reference:
            style_path = style_manager.get_style_path(style_reference)

        # Build generation config
        gen_config = GenerationConfig(
            prompt=full_prompt,
            resolution=Resolution(resolution),
            aspect_ratio=AspectRatio(aspect_ratio),
            temperature=temperature,
            style_reference_path=style_path,
        )

        # Generate
        img_provider = get_provider(provider, api_key, model=provider_config.model)
        result = await img_provider.generate(gen_config)

        elapsed_ms = int((time.monotonic() - start) * 1000)

        # Save image
        saved_path = None
        if result.success and result.image_data:
            if output_path:
                save_to = Path(output_path).expanduser()
            else:
                output_dir = Path(config.output_directory).expanduser()
                output_dir.mkdir(parents=True, exist_ok=True)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                save_to = output_dir / f"{diagram_type}_{timestamp}.png"

            save_to.parent.mkdir(parents=True, exist_ok=True)
            save_to.write_bytes(result.image_data)
            saved_path = str(save_to)
            result.output_path = saved_path

        # Track cost
        cost_tracker.record(
            GenerationRecord(
                provider=provider,
                model=provider_config.model,
                diagram_type=diagram_type,
                resolution=resolution,
                aspect_ratio=aspect_ratio,
                tokens_used=result.tokens_used,
                cost_usd=result.cost_usd,
                billing_model=result.billing_model.value,
                generation_time_ms=elapsed_ms,
                success=result.success,
                output_path=saved_path,
                template_used=diagram_type,
                style_used=style_reference,
                error_message=result.error_message,
            )
        )

        response = _serialize(result)
        response["status"] = "success" if result.success else "error"
        if saved_path:
            response["output_path"] = saved_path
        return response

    # --- Tool: edit_diagram ---

    @app.tool()
    async def edit_diagram(
        image_path: str,
        prompt: str,
        provider: str = "gemini",
        resolution: str | None = None,
        reference_images: list[str] | None = None,
        output_path: str | None = None,
    ) -> dict:
        """Edit an existing diagram based on instructions.

        Args:
            image_path: Path to the existing diagram image
            prompt: Edit instructions
            provider: Image generation provider (gemini|openai|replicate)
            resolution: Output resolution (auto-detect if not specified)
            reference_images: Additional reference image paths
            output_path: Where to save the result
        """
        start = time.monotonic()

        # Load input image
        img_path = Path(image_path).expanduser()
        if not img_path.exists():
            return {"status": "error", "error": f"Image not found: {image_path}"}
        input_image = img_path.read_bytes()

        # Resolve provider
        provider_config = config.providers.get(provider)
        if not provider_config:
            return {"status": "error", "error": f"Provider '{provider}' not configured"}

        api_key = resolve_api_key(provider_config)
        if not api_key:
            return {
                "status": "error",
                "error": f"No API key for provider '{provider}'. "
                f"Set {provider_config.api_key_env} environment variable.",
            }

        # Check provider supports editing
        img_provider = get_provider(provider, api_key, model=provider_config.model)
        if "edit" not in img_provider.supported_features():
            return {
                "status": "error",
                "error": f"Provider '{provider}' does not support image editing",
            }

        # Build config
        ref_paths = [Path(p).expanduser() for p in (reference_images or [])]
        gen_config = GenerationConfig(
            prompt=prompt,
            resolution=Resolution(resolution) if resolution else Resolution.RES_2K,
            reference_images=ref_paths,
        )

        result = await img_provider.edit(input_image, gen_config)
        elapsed_ms = int((time.monotonic() - start) * 1000)

        # Save result
        saved_path = None
        if result.success and result.image_data:
            if output_path:
                save_to = Path(output_path).expanduser()
            else:
                output_dir = Path(config.output_directory).expanduser()
                output_dir.mkdir(parents=True, exist_ok=True)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                save_to = output_dir / f"edit_{timestamp}.png"

            save_to.parent.mkdir(parents=True, exist_ok=True)
            save_to.write_bytes(result.image_data)
            saved_path = str(save_to)

        # Track cost
        cost_tracker.record(
            GenerationRecord(
                provider=provider,
                model=provider_config.model,
                diagram_type="edit",
                resolution=resolution or "2K",
                cost_usd=result.cost_usd,
                billing_model=result.billing_model.value,
                generation_time_ms=elapsed_ms,
                success=result.success,
                output_path=saved_path,
                error_message=result.error_message,
            )
        )

        response = _serialize(result)
        response["status"] = "success" if result.success else "error"
        if saved_path:
            response["output_path"] = saved_path
        return response

    # --- Tool: list_templates ---

    @app.tool()
    async def list_templates() -> dict:
        """List all available diagram templates with descriptions."""
        templates = load_all_templates()
        return {
            "status": "success",
            "templates": [
                {
                    "name": t.name,
                    "display_name": t.display_name,
                    "description": t.description,
                    "supports": t.supports,
                    "variables": t.variables,
                }
                for t in templates.values()
            ],
            "count": len(templates),
        }

    # --- Tool: list_providers ---

    @app.tool()
    async def list_providers() -> dict:
        """List configured providers with status, models, and health information."""
        providers_info = []
        for name, pconfig in config.providers.items():
            api_key = resolve_api_key(pconfig)
            has_key = bool(api_key)
            features = []
            if has_key and name in PROVIDER_MAP:
                try:
                    p = get_provider(name, api_key, model=pconfig.model)
                    features = sorted(p.supported_features())
                    pricing = _serialize(p.get_pricing())
                except Exception:
                    pricing = None
            else:
                pricing = None

            providers_info.append({
                "name": name,
                "enabled": pconfig.enabled,
                "model": pconfig.model,
                "api_key_configured": has_key,
                "api_key_env": pconfig.api_key_env,
                "features": features,
                "pricing": pricing,
            })

        return {
            "status": "success",
            "providers": providers_info,
            "default_provider": config.default_provider.value,
        }

    # --- Tool: list_styles ---

    @app.tool()
    async def list_styles() -> dict:
        """List all available style reference images."""
        styles = style_manager.list_styles()
        return {
            "status": "success",
            "styles": [
                {
                    "name": s.name,
                    "display_name": s.display_name,
                    "description": s.description,
                    "path": str(s.path),
                    "tags": s.tags,
                }
                for s in styles
            ],
            "count": len(styles),
        }

    # --- Tool: get_usage_report ---

    @app.tool()
    async def get_usage_report(
        days: int = 30,
        group_by: str = "provider",
    ) -> dict:
        """Get usage and cost report for diagram generations.

        Args:
            days: Number of days to report on (default: 30)
            group_by: Group results by 'provider', 'diagram_type', or 'day'
        """
        report = cost_tracker.get_usage_report(days=days, group_by=group_by)
        return {
            "status": "success",
            **_serialize(report),
        }

    # --- Tool: configure_provider ---

    @app.tool()
    async def configure_provider(
        provider: str,
        api_key: str,
    ) -> dict:
        """Configure an API key for a provider (sets environment variable for current session).

        Args:
            provider: Provider name (gemini|openai|replicate)
            api_key: The API key to set
        """
        import os

        provider_config = config.providers.get(provider)
        if not provider_config:
            return {"status": "error", "error": f"Unknown provider: {provider}"}

        # Set the environment variable
        os.environ[provider_config.api_key_env] = api_key

        # Verify connectivity
        try:
            img_provider = get_provider(provider, api_key, model=provider_config.model)
            health = await img_provider.health_check()
            return {
                "status": "success" if health.available else "warning",
                "message": f"API key set for {provider} ({provider_config.api_key_env})",
                "health": _serialize(health),
            }
        except Exception as e:
            return {
                "status": "warning",
                "message": f"API key set for {provider}, but health check failed: {e}",
            }

    return app


def main() -> None:
    """Run the Diagram Forge MCP server over stdio."""
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
