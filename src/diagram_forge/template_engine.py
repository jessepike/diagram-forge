"""Template engine for loading YAML templates and merging with user content."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from diagram_forge.models import DiagramTemplate, DiagramType, GlobalDesignTokens

if TYPE_CHECKING:
    pass

TEMPLATES_DIR = Path(__file__).parent / "templates"

_cached_tokens: GlobalDesignTokens | None = None


def _get_default_tokens() -> GlobalDesignTokens:
    """Load and cache the default design tokens."""
    global _cached_tokens
    if _cached_tokens is None:
        try:
            from diagram_forge.config import load_design_tokens
            _cached_tokens = load_design_tokens()
        except Exception:
            _cached_tokens = GlobalDesignTokens()
    return _cached_tokens


def build_global_style_block(tokens: GlobalDesignTokens) -> str:
    """Render global design tokens as a concise prompt instruction block."""
    a = tokens.aesthetic
    t = tokens.typography
    c = tokens.colors
    r = tokens.rendering

    no_list = []
    if not a.shadows:
        no_list.append("NO shadows")
    if not a.gradients:
        no_list.append("NO gradients")
    if a.flat:
        no_list.append("NO 3D effects")
    no_clause = ", ".join(no_list) if no_list else "clean rendering"

    return (
        f"GLOBAL DESIGN STANDARDS (apply to all elements):\n"
        f"- Aesthetic: {a.style}, flat — {no_clause}, NO decorative embellishment\n"
        f"- Typography: {t.font} — title {t.title_size} {t.weight}, "
        f"headings {t.heading_size}, body {t.body_size}, minimum {t.min_readable_size}\n"
        f"- Background: {c.background} | Surfaces/cards: {c.surface}\n"
        f"- Borders: {r.border_style} {c.border} (emphasis: {c.border_strong})\n"
        f"- Text: {c.text_primary} primary | {c.text_secondary} secondary\n"
        f"- Accent: {c.accent} for highlights and key elements | Muted accent: {c.accent_muted}\n"
        f"- Status colors: positive {c.positive} | warning {c.warning} | negative {c.negative}\n"
        f"- Corners: {r.corners} | Arrows: {r.arrow_color}, {r.arrow_style}\n"
        f"- Icons: {r.icon_style} | Whitespace: {a.whitespace} — generous padding between elements"
    )


def load_template(template_name: str) -> DiagramTemplate:
    """Load a single template by name from the templates directory."""
    path = TEMPLATES_DIR / f"{template_name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {template_name} (looked at {path})")

    with open(path) as f:
        raw = yaml.safe_load(f)

    return DiagramTemplate(**raw)


def load_all_templates() -> dict[str, DiagramTemplate]:
    """Load all available templates."""
    templates = {}
    if not TEMPLATES_DIR.exists():
        return templates

    for path in sorted(TEMPLATES_DIR.glob("*.yaml")):
        try:
            with open(path) as f:
                raw = yaml.safe_load(f)
            template = DiagramTemplate(**raw)
            templates[template.name] = template
        except Exception:
            continue

    return templates


def render_prompt(
    template: DiagramTemplate,
    user_variables: dict[str, str] | None = None,
    extra_instructions: str = "",
    design_tokens: GlobalDesignTokens | None = None,
) -> str:
    """Render a template's prompt with user-provided variables.

    Substitutes {variable_name} placeholders in the prompt_template
    with values from user_variables, template defaults, and style defaults.
    """
    tokens = design_tokens or _get_default_tokens()
    variables = dict(template.variables)
    if user_variables:
        variables.update(user_variables)

    # Inject global style block — templates can place {global_style_block} explicitly
    variables.setdefault("global_style_block", build_global_style_block(tokens))

    # Build style defaults block
    sd = template.style_defaults
    style_block = (
        f"STYLE: {sd.background} background, {sd.font} font, "
        f"{sd.corners} corners, {sd.borders} borders."
    )
    variables.setdefault("style_defaults_block", style_block)
    variables.setdefault("aspect_ratio", sd.aspect_ratio)
    variables.setdefault("resolution", "2K")

    # Build color system block if present
    if template.color_system:
        cs = template.color_system
        palette_lines = "\n".join(
            f"  - {role}: {color}" for role, color in cs.palette.items()
        )
        color_block = f"{cs.description}\n{palette_lines}"
        variables.setdefault("color_system_block", color_block)
    else:
        variables.setdefault("color_system_block", "")

    # Build legend block from color system if not provided
    if "legend_block" not in variables and template.color_system:
        legend_lines = [
            f"  {color} = {role}" for role, color in template.color_system.palette.items()
        ]
        variables["legend_block"] = "\n".join(legend_lines)

    # Render template
    prompt = template.prompt_template
    for key, value in variables.items():
        prompt = prompt.replace(f"{{{key}}}", str(value))

    # Append extra instructions
    if extra_instructions:
        prompt = f"{prompt}\n\n{extra_instructions}"

    return prompt


def build_prompt(
    diagram_type: str,
    user_prompt: str,
    user_variables: dict[str, str] | None = None,
    resolution: str = "2K",
    aspect_ratio: str = "16:9",
    design_tokens: GlobalDesignTokens | None = None,
) -> str:
    """High-level prompt builder: loads template, merges user content, returns final prompt.

    Global design tokens are injected as a preamble on all prompts.
    Templates that include {global_style_block} control placement; others get it prepended.
    If the diagram_type template doesn't exist or is 'generic', uses user_prompt directly.
    """
    tokens = design_tokens or _get_default_tokens()
    global_block = build_global_style_block(tokens)

    try:
        template = load_template(diagram_type)
    except FileNotFoundError:
        # Fall back to generic formatting with global tokens prepended
        return (
            f"{global_block}\n\n"
            f"{user_prompt}\n\n"
            f"All text crystal clear and perfectly legible. Enterprise presentation quality.\n"
            f"{aspect_ratio} aspect ratio. {resolution} resolution."
        )

    # Merge user variables
    vars_dict = dict(user_variables or {})
    vars_dict.setdefault("resolution", resolution)
    vars_dict.setdefault("aspect_ratio", aspect_ratio)

    rendered = render_prompt(
        template,
        vars_dict,
        extra_instructions=user_prompt if user_prompt else "",
        design_tokens=tokens,
    )

    # If the template already consumed {global_style_block}, it's embedded inline.
    # Otherwise prepend it so every prompt gets the global standards.
    if "{global_style_block}" in template.prompt_template:
        return rendered
    return f"{global_block}\n\n{rendered}"
