"""Tests for collection page generation, nav integration, and search."""

from pathlib import Path

from jinja2 import DictLoader, Environment

from rockgarden.config import CollectionConfig, Config
from rockgarden.content.collection import (
    Collection,
    generate_collection_url,
    get_collection_skip_slugs,
)
from rockgarden.content.models import Page
from rockgarden.output.builder import build_collection_pages


def make_page(rel_path: str, slug: str, **frontmatter) -> Page:
    return Page(
        source_path=Path(rel_path),
        slug=slug,
        frontmatter=frontmatter,
        content="",
    )


class TestGenerateCollectionUrl:
    def test_dict_entry(self):
        entry = {"slug": "dave", "name": "Dave Forgac"}
        url = generate_collection_url("/speakers/{slug}/", entry)
        assert url == "/speakers/dave/"

    def test_page_entry_uses_stem(self):
        page = Page(
            source_path=Path("speakers/dave-forgac.md"),
            slug="speakers/dave-forgac",
            frontmatter={"name": "Dave"},
            content="",
        )
        url = generate_collection_url("/speakers/{slug}/", page)
        assert url == "/speakers/dave-forgac/"

    def test_multiple_fields(self):
        entry = {"year": "2026", "slug": "keynote"}
        url = generate_collection_url("/talks/{year}/{slug}/", entry)
        assert url == "/talks/2026/keynote/"

    def test_frontmatter_field_in_page(self):
        page = Page(
            source_path=Path("talks/keynote.md"),
            slug="talks/keynote",
            frontmatter={"year": "2026"},
            content="",
        )
        url = generate_collection_url("/talks/{year}/{slug}/", page)
        assert url == "/talks/2026/keynote/"


class TestGetCollectionSkipSlugs:
    def test_no_collections(self):
        assert get_collection_skip_slugs({}) == set()

    def test_collection_without_template(self):
        """Pages in a namespace-only collection are NOT skipped."""
        page = make_page("chars/alice.md", "chars/alice")
        cfg = CollectionConfig(name="chars", source="chars")
        col = Collection(name="chars", config=cfg, entries=[page])
        skip = get_collection_skip_slugs({"chars": col})
        assert skip == set()

    def test_collection_with_template_and_url(self):
        """Pages in a page-generating collection ARE skipped."""
        page = make_page("speakers/dave.md", "speakers/dave")
        cfg = CollectionConfig(
            name="speakers",
            source="speakers",
            template="speaker.html",
            url_pattern="/speakers/{slug}/",
        )
        col = Collection(name="speakers", config=cfg, entries=[page])
        skip = get_collection_skip_slugs({"speakers": col})
        assert "speakers/dave" in skip

    def test_pages_false(self):
        """Pages in a pages=false collection ARE skipped."""
        page = make_page("schedule/day1.md", "schedule/day1")
        cfg = CollectionConfig(name="schedule", source="schedule", pages=False)
        col = Collection(name="schedule", config=cfg, entries=[page])
        skip = get_collection_skip_slugs({"schedule": col})
        assert "schedule/day1" in skip

    def test_dict_entries_not_in_skip(self):
        """Dict entries don't have slugs to skip."""
        cfg = CollectionConfig(
            name="speakers",
            source="speakers",
            template="speaker.html",
            url_pattern="/speakers/{slug}/",
        )
        col = Collection(
            name="speakers",
            config=cfg,
            entries=[{"slug": "dave", "name": "Dave"}],
        )
        skip = get_collection_skip_slugs({"speakers": col})
        assert skip == set()


class TestBuildCollectionPages:
    def _make_env(self, template_content):
        loader = DictLoader(
            {
                "speaker.html": template_content,
                "layouts/default.html": "{% block content %}{% endblock %}",
            }
        )
        return Environment(loader=loader, autoescape=True)

    def test_generates_pages(self, tmp_path):
        env = self._make_env("{{ entry.name }} - {{ entry.slug }}")
        cfg = CollectionConfig(
            name="speakers",
            source="speakers",
            template="speaker.html",
            url_pattern="/speakers/{slug}/",
        )
        col = Collection(
            name="speakers",
            config=cfg,
            entries=[
                {"slug": "alice", "name": "Alice"},
                {"slug": "bob", "name": "Bob"},
            ],
        )
        config = Config()

        generated = build_collection_pages(
            {"speakers": col},
            env,
            {},
            tmp_path,
            clean_urls=True,
            base_path="",
            config=config,
        )

        assert len(generated) == 2
        alice_file = tmp_path / "speakers" / "alice" / "index.html"
        assert alice_file.exists()
        assert "Alice" in alice_file.read_text()

        bob_file = tmp_path / "speakers" / "bob" / "index.html"
        assert bob_file.exists()
        assert "Bob" in bob_file.read_text()

    def test_correct_output_paths_no_clean_urls(self, tmp_path):
        env = self._make_env("{{ entry.name }}")
        cfg = CollectionConfig(
            name="speakers",
            source="speakers",
            template="speaker.html",
            url_pattern="/speakers/{slug}/",
        )
        col = Collection(
            name="speakers",
            config=cfg,
            entries=[{"slug": "alice", "name": "Alice"}],
        )
        config = Config()

        build_collection_pages(
            {"speakers": col},
            env,
            {},
            tmp_path,
            clean_urls=False,
            base_path="",
            config=config,
        )

        assert (tmp_path / "speakers" / "alice.html").exists()

    def test_pages_false_no_output(self, tmp_path):
        env = self._make_env("{{ entry.name }}")
        cfg = CollectionConfig(
            name="schedule",
            source="schedule",
            pages=False,
        )
        col = Collection(
            name="schedule",
            config=cfg,
            entries=[{"slug": "day1", "name": "Day 1"}],
        )
        config = Config()

        generated = build_collection_pages(
            {"schedule": col},
            env,
            {},
            tmp_path,
            clean_urls=True,
            base_path="",
            config=config,
        )

        assert generated == []

    def test_no_template_no_output(self, tmp_path):
        """Collection without template doesn't generate pages."""
        env = self._make_env("{{ entry.name }}")
        cfg = CollectionConfig(name="chars", source="chars")
        col = Collection(
            name="chars",
            config=cfg,
            entries=[{"slug": "alice", "name": "Alice"}],
        )
        config = Config()

        generated = build_collection_pages(
            {"chars": col},
            env,
            {},
            tmp_path,
            clean_urls=True,
            base_path="",
            config=config,
        )

        assert generated == []

    def test_entry_data_in_template(self, tmp_path):
        env = self._make_env("name={{ entry.name }} bio={{ entry.bio }}")
        cfg = CollectionConfig(
            name="speakers",
            source="speakers",
            template="speaker.html",
            url_pattern="/speakers/{slug}/",
        )
        col = Collection(
            name="speakers",
            config=cfg,
            entries=[
                {
                    "slug": "dave",
                    "name": "Dave",
                    "bio": "Pythonista",
                }
            ],
        )
        config = Config()

        build_collection_pages(
            {"speakers": col},
            env,
            {},
            tmp_path,
            clean_urls=True,
            base_path="",
            config=config,
        )

        content = (tmp_path / "speakers" / "dave" / "index.html").read_text()
        assert "name=Dave" in content
        assert "bio=Pythonista" in content

    def test_page_entry_with_custom_template(self, tmp_path):
        """Markdown pages in a collection use the collection template."""
        env = self._make_env("page: {{ entry.title }}")
        page = Page(
            source_path=Path("speakers/alice.md"),
            slug="speakers/alice",
            frontmatter={"title": "Alice Talk"},
            content="Hello world",
        )
        cfg = CollectionConfig(
            name="speakers",
            source="speakers",
            template="speaker.html",
            url_pattern="/speakers/{slug}/",
        )
        col = Collection(name="speakers", config=cfg, entries=[page])
        config = Config()

        generated = build_collection_pages(
            {"speakers": col},
            env,
            {},
            tmp_path,
            clean_urls=True,
            base_path="",
            config=config,
        )

        assert len(generated) == 1
        content = (tmp_path / "speakers" / "alice" / "index.html").read_text()
        assert "page: Alice Talk" in content

    def test_generated_entries_for_search(self, tmp_path):
        """build_collection_pages returns search-ready entries."""
        env = self._make_env("{{ entry.name }}")
        cfg = CollectionConfig(
            name="speakers",
            source="speakers",
            template="speaker.html",
            url_pattern="/speakers/{slug}/",
        )
        col = Collection(
            name="speakers",
            config=cfg,
            entries=[{"slug": "dave", "name": "Dave"}],
        )
        config = Config()

        generated = build_collection_pages(
            {"speakers": col},
            env,
            {},
            tmp_path,
            clean_urls=True,
            base_path="",
            config=config,
        )

        assert len(generated) == 1
        assert generated[0]["title"] == "Dave"
        assert generated[0]["url"] == "/speakers/dave/"
        assert generated[0]["collection"] == "speakers"

    def test_base_path_in_url(self, tmp_path):
        env = self._make_env("{{ entry.name }}")
        cfg = CollectionConfig(
            name="speakers",
            source="speakers",
            template="speaker.html",
            url_pattern="/speakers/{slug}/",
        )
        col = Collection(
            name="speakers",
            config=cfg,
            entries=[{"slug": "dave", "name": "Dave"}],
        )
        config = Config()

        generated = build_collection_pages(
            {"speakers": col},
            env,
            {},
            tmp_path,
            clean_urls=True,
            base_path="/docs",
            config=config,
        )

        assert generated[0]["url"] == "/docs/speakers/dave/"
