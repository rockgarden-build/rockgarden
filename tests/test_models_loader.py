"""Tests for content model resolution and validation."""

from pathlib import Path

import pytest
from pydantic import BaseModel

from rockgarden.content.models import Page
from rockgarden.content.models_loader import resolve_model, validate_entry


def _write_model(
    path: Path,
    class_name: str,
    fields: str = 'name: str\n    bio: str = ""',
):
    """Helper to write a model Python file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"from pydantic import BaseModel\n\n"
        f"class {class_name}(BaseModel):\n"
        f"    {fields}\n"
    )


class TestResolveModel:
    def test_site_level_model(self, tmp_path):
        _write_model(tmp_path / "_models" / "speaker.py", "Speaker")
        cls = resolve_model("speaker", tmp_path)
        assert cls is not None
        assert issubclass(cls, BaseModel)
        assert cls.__name__ == "Speaker"

    def test_theme_level_fallback(self, tmp_path):
        _write_model(
            tmp_path / "_themes" / "mytheme" / "_models" / "speaker.py", "Speaker"
        )
        cls = resolve_model("speaker", tmp_path, theme_name="mytheme")
        assert cls is not None
        assert cls.__name__ == "Speaker"

    def test_site_takes_precedence_over_theme(self, tmp_path):
        fields = 'name: str\n    level: int = 1'
        _write_model(
            tmp_path / "_models" / "speaker.py",
            "Speaker",
            fields,
        )
        _write_model(
            tmp_path / "_themes" / "mytheme" / "_models" / "speaker.py",
            "Speaker",
            'name: str\n    level: int = 99',
        )
        cls = resolve_model("speaker", tmp_path, theme_name="mytheme")
        instance = cls(name="test")
        assert instance.level == 1  # site-level default, not theme

    def test_missing_model_returns_none(self, tmp_path):
        cls = resolve_model("nonexistent", tmp_path)
        assert cls is None

    def test_wrong_class_name_raises(self, tmp_path):
        path = tmp_path / "_models" / "speaker.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "from pydantic import BaseModel\n\n"
            "class WrongName(BaseModel):\n"
            "    name: str\n"
        )
        with pytest.raises(ValueError, match="does not define class 'Speaker'"):
            resolve_model("speaker", tmp_path)

    def test_not_basemodel_raises(self, tmp_path):
        path = tmp_path / "_models" / "speaker.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("class Speaker:\n    pass\n")
        with pytest.raises(ValueError, match="must be a Pydantic BaseModel"):
            resolve_model("speaker", tmp_path)

    def test_underscore_model_name(self, tmp_path):
        """Model name 'player_character' → class 'PlayerCharacter'."""
        _write_model(
            tmp_path / "_models" / "player_character.py",
            "PlayerCharacter",
            "name: str\n    level: int = 1",
        )
        cls = resolve_model("player_character", tmp_path)
        assert cls is not None
        assert cls.__name__ == "PlayerCharacter"


class TestValidateEntry:
    def _make_model(self):
        class Speaker(BaseModel):
            name: str
            bio: str = ""
            level: int = 1

        return Speaker

    def test_validate_dict_entry(self):
        model = self._make_model()
        entry = {"name": "Alice", "slug": "alice"}
        instance = validate_entry(entry, model, "speakers")
        assert instance.name == "Alice"
        assert instance.bio == ""
        assert entry["bio"] == ""  # default merged back

    def test_validate_page_entry(self):
        model = self._make_model()
        page = Page(
            source_path=Path("speakers/alice.md"),
            slug="speakers/alice",
            frontmatter={"name": "Alice", "level": "5"},
            content="",
        )
        instance = validate_entry(page, model, "speakers")
        assert instance.name == "Alice"
        assert instance.level == 5  # coerced from str
        assert page.frontmatter["level"] == 5  # merged back

    def test_validation_failure(self):
        model = self._make_model()
        entry = {"slug": "missing-name"}  # 'name' is required
        with pytest.raises(
            ValueError, match="Validation error.*speakers.*missing-name"
        ):
            validate_entry(entry, model, "speakers")

    def test_pydantic_coercion(self):
        model = self._make_model()
        entry = {"name": "Bob", "level": "42", "slug": "bob"}
        validate_entry(entry, model, "speakers")
        assert entry["level"] == 42

    def test_pydantic_defaults_applied(self):
        model = self._make_model()
        entry = {"name": "Charlie", "slug": "charlie"}
        validate_entry(entry, model, "speakers")
        assert entry["bio"] == ""
        assert entry["level"] == 1
