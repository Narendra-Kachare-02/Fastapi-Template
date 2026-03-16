"""Helpers for loading prompt templates from the prompts folder."""

from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_template(name: str) -> str:
    """Load a template by name (without extension). Looks for name.txt in prompts dir."""
    path = PROMPTS_DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {name}")
    return path.read_text().strip()


def load_prompt(name: str) -> str:
    """Backwards-compatible helper: alias for load_template."""
    return load_template(name)

