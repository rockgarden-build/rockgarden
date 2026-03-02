"""Resolve and validate Pydantic content models for collections."""

import importlib.util
import sys
from pathlib import Path

from pydantic import BaseModel, ValidationError

from rockgarden.content.models import Page


def _model_class_name(model_name: str) -> str:
    """Derive class name from model name.

    E.g. 'speaker' → 'Speaker', 'player_character' → 'PlayerCharacter'.
    """
    return "".join(part.capitalize() for part in model_name.split("_"))


def resolve_model(
    model_name: str,
    site_root: Path,
    theme_name: str = "",
) -> type[BaseModel] | None:
    """Resolve a model name to a Pydantic BaseModel class.

    Cascade (first match wins):
    1. ``_models/<name>.py`` — site-level
    2. ``_themes/<theme>/_models/<name>.py`` — theme-provided

    Args:
        model_name: The model name (e.g. ``"speaker"``).
        site_root: Root directory of the site.
        theme_name: Active theme name, if any.

    Returns:
        The BaseModel subclass, or None if no model file exists.

    Raises:
        ValueError: If the file exists but doesn't contain the expected class.
    """
    candidates = [site_root / "_models" / f"{model_name}.py"]
    if theme_name:
        candidates.append(
            site_root / "_themes" / theme_name / "_models" / f"{model_name}.py"
        )

    expected_class = _model_class_name(model_name)

    for path in candidates:
        if not path.exists():
            continue

        module_name = f"_rockgarden_models_{model_name}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            continue

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        cls = getattr(module, expected_class, None)
        if cls is None:
            raise ValueError(
                f"Model file {path} does not define class '{expected_class}'"
            )
        if not (isinstance(cls, type) and issubclass(cls, BaseModel)):
            raise ValueError(
                f"Class '{expected_class}' in {path} "
                f"must be a Pydantic BaseModel subclass"
            )
        return cls

    return None


def validate_entry(
    entry: Page | dict,
    model_class: type[BaseModel],
    collection_name: str,
) -> BaseModel:
    """Validate a collection entry against a Pydantic model.

    For Page entries, validates the frontmatter dict. For dict entries, validates
    the dict directly. Pydantic defaults and coercion are applied.

    Args:
        entry: The entry to validate (Page or dict).
        model_class: The Pydantic BaseModel class to validate against.
        collection_name: Collection name for error context.

    Returns:
        The validated Pydantic model instance.

    Raises:
        ValueError: If validation fails, with context about which entry failed.
    """
    if isinstance(entry, Page):
        data = entry.frontmatter
        entry_id = entry.slug
    else:
        data = entry
        entry_id = entry.get("slug", "<unknown>")

    try:
        instance = model_class.model_validate(data)
    except ValidationError as exc:
        raise ValueError(
            f"Validation error in collection '{collection_name}', "
            f"entry '{entry_id}':\n{exc}"
        ) from exc

    validated = instance.model_dump()
    if isinstance(entry, Page):
        entry.frontmatter.update(validated)
    else:
        entry.update(validated)

    return instance
