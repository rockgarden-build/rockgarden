"""Tests for non-markdown data file loading."""

import json

import pytest
import yaml

from rockgarden.content.format_loader import load_collection_data_files, load_data_file


class TestLoadDataFile:
    def test_load_yaml(self, tmp_path):
        f = tmp_path / "speaker.yaml"
        f.write_text(yaml.dump({"name": "Alice", "bio": "Speaker"}))
        data = load_data_file(f)
        assert data == {"name": "Alice", "bio": "Speaker"}

    def test_load_yml(self, tmp_path):
        f = tmp_path / "speaker.yml"
        f.write_text(yaml.dump({"name": "Bob"}))
        data = load_data_file(f)
        assert data["name"] == "Bob"

    def test_load_json(self, tmp_path):
        f = tmp_path / "speaker.json"
        f.write_text(json.dumps({"name": "Charlie", "talks": 3}))
        data = load_data_file(f)
        assert data == {"name": "Charlie", "talks": 3}

    def test_load_toml(self, tmp_path):
        f = tmp_path / "speaker.toml"
        f.write_text('name = "Dana"\nlevel = 5\n')
        data = load_data_file(f)
        assert data == {"name": "Dana", "level": 5}

    def test_unsupported_format(self, tmp_path):
        f = tmp_path / "data.xml"
        f.write_text("<data/>")
        with pytest.raises(ValueError, match="Unsupported"):
            load_data_file(f)

    def test_non_dict_yaml_raises(self, tmp_path):
        f = tmp_path / "list.yaml"
        f.write_text("- item1\n- item2\n")
        with pytest.raises(ValueError, match="must contain a mapping"):
            load_data_file(f)

    def test_non_dict_json_raises(self, tmp_path):
        f = tmp_path / "list.json"
        f.write_text('["a", "b"]')
        with pytest.raises(ValueError, match="must contain a mapping"):
            load_data_file(f)


class TestLoadCollectionDataFiles:
    def test_load_mixed_formats(self, tmp_path):
        source = tmp_path / "content"
        data_dir = source / "speakers"
        data_dir.mkdir(parents=True)

        (data_dir / "alice.yaml").write_text(yaml.dump({"name": "Alice"}))
        (data_dir / "bob.json").write_text(json.dumps({"name": "Bob"}))
        (data_dir / "charlie.toml").write_text('name = "Charlie"\n')

        entries = load_collection_data_files(source, "speakers")
        assert len(entries) == 3
        names = {e["name"] for e in entries}
        assert names == {"Alice", "Bob", "Charlie"}

    def test_slug_from_filename(self, tmp_path):
        source = tmp_path / "content"
        data_dir = source / "speakers"
        data_dir.mkdir(parents=True)

        (data_dir / "dave-forgac.yaml").write_text(yaml.dump({"name": "Dave"}))

        entries = load_collection_data_files(source, "speakers")
        assert entries[0]["slug"] == "dave-forgac"

    def test_explicit_slug_preserved(self, tmp_path):
        source = tmp_path / "content"
        data_dir = source / "speakers"
        data_dir.mkdir(parents=True)

        (data_dir / "speaker1.yaml").write_text(
            yaml.dump({"name": "Alice", "slug": "custom-slug"})
        )

        entries = load_collection_data_files(source, "speakers")
        assert entries[0]["slug"] == "custom-slug"

    def test_missing_directory(self, tmp_path):
        source = tmp_path / "content"
        source.mkdir()
        entries = load_collection_data_files(source, "nonexistent")
        assert entries == []

    def test_ignores_non_data_files(self, tmp_path):
        source = tmp_path / "content"
        data_dir = source / "speakers"
        data_dir.mkdir(parents=True)

        (data_dir / "alice.yaml").write_text(yaml.dump({"name": "Alice"}))
        (data_dir / "notes.md").write_text("# Notes")
        (data_dir / "image.png").write_bytes(b"fake image")

        entries = load_collection_data_files(source, "speakers")
        assert len(entries) == 1
        assert entries[0]["name"] == "Alice"

    def test_nested_data_files(self, tmp_path):
        source = tmp_path / "content"
        sub_dir = source / "data" / "nested"
        sub_dir.mkdir(parents=True)

        (sub_dir / "item.yaml").write_text(yaml.dump({"name": "Nested"}))

        entries = load_collection_data_files(source, "data")
        assert len(entries) == 1
        assert entries[0]["name"] == "Nested"


class TestMixedMarkdownAndData:
    def test_collection_with_both(self, tmp_path):
        """Collections can have both markdown pages and data files."""
        from rockgarden.config import CollectionConfig
        from rockgarden.content.collection import partition_collections
        from rockgarden.content.models import Page

        source = tmp_path / "content"
        chars_dir = source / "characters"
        chars_dir.mkdir(parents=True)

        md_file = chars_dir / "alice.md"
        md_file.write_text("---\ntitle: Alice\n---\nAlice is a character.")

        (chars_dir / "bob.yaml").write_text(yaml.dump({"name": "Bob", "role": "NPC"}))

        pages = [
            Page(
                source_path=md_file,
                slug="characters/alice",
                frontmatter={"title": "Alice"},
                content="Alice is a character.",
            )
        ]
        configs = [CollectionConfig(name="characters", source="characters")]
        collections = partition_collections(pages, configs, source)

        data_entries = load_collection_data_files(source, "characters")
        collections["characters"].entries.extend(data_entries)

        entries = collections["characters"].entries
        assert len(entries) == 2
        assert isinstance(entries[0], Page)
        assert isinstance(entries[1], dict)
        assert entries[1]["name"] == "Bob"
