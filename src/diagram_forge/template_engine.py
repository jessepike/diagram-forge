"""Template engine for loading YAML templates and merging with user content."""

from __future__ import annotations

from pathlib import Path

import yaml

from diagram_forge.models import DiagramTemplate, DiagramType

TEMPLATES_DIR = Path(__file__).parent / "templates"


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
) -> str:
    """Render a template's prompt with user-provided variables.

    Substitutes {variable_name} placeholders in the prompt_template
    with values from user_variables, template defaults, and style defaults.
    """
    variables = dict(template.variables)
    if user_variables:
        variables.update(user_variables)

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
) -> str:
    """High-level prompt builder: loads template, merges user content, returns final prompt.

    If the diagram_type template doesn't exist or is 'generic', uses user_prompt directly
    with basic formatting additions.
    """
    try:
        template = load_template(diagram_type)
    except FileNotFoundError:
        # Fall back to generic formatting
        return (
            f"{user_prompt}\n\n"
            f"All text crystal clear and perfectly legible. Enterprise presentation quality.\n"
            f"{aspect_ratio} aspect ratio. {resolution} resolution."
        )

    # Merge user variables
    vars_dict = dict(user_variables or {})
    vars_dict.setdefault("resolution", resolution)
    vars_dict.setdefault("aspect_ratio", aspect_ratio)

    # If user provided a prompt, use it as the main content
    if user_prompt and diagram_type != "generic":
        return render_prompt(template, vars_dict, extra_instructions=user_prompt)
    elif user_prompt:
        return render_prompt(template, vars_dict, extra_instructions=user_prompt)
    else:
        return render_prompt(template, vars_dict)
