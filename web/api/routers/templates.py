"""GET /templates — returns all available diagram templates."""

from __future__ import annotations

from fastapi import APIRouter

from diagram_forge.template_engine import load_all_templates

router = APIRouter()


@router.get("/templates")
async def list_templates() -> list[dict]:
    """Return all available templates with key metadata."""
    templates = load_all_templates()
    return [
        {
            "id": t.name,
            "name": t.display_name,
            "description": t.description,
            "recommended_provider": t.recommended_provider,
        }
        for t in templates.values()
    ]
