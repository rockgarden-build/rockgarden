"""Tests for Unicode normalization in content store."""

import unicodedata
from pathlib import Path

from rockgarden.content.models import Page
from rockgarden.content.store import ContentStore


class TestUnicodeNormalization:
    """Test that ContentStore handles Unicode normalization correctly."""

    def test_nfc_filename_found_with_nfc_lookup(self):
        """Should find page with NFC filename using NFC lookup."""
        # Create a page with NFC (composed) characters
        page = Page(
            source_path=Path("Orontinórë.md"),
            slug="orotinore",
            frontmatter={},
            content="",
        )
        store = ContentStore([page])

        # Lookup with NFC (same normalization)
        result = store.get_by_name("Orontinórë")

        assert result is not None
        assert result == page

    def test_nfd_filename_found_with_nfc_lookup(self):
        """Should find page with NFD filename using NFC lookup."""
        # Create NFD (decomposed) version - 'ó' = 'o' + combining accent
        nfd_name = unicodedata.normalize('NFD', "Orontinórë")
        page = Page(
            source_path=Path(f"{nfd_name}.md"),
            slug="orotinore",
            frontmatter={},
            content="",
        )
        store = ContentStore([page])

        # Lookup with NFC (composed) version
        nfc_name = unicodedata.normalize('NFC', "Orontinórë")
        result = store.get_by_name(nfc_name)

        assert result is not None
        assert result == page

    def test_nfc_filename_found_with_nfd_lookup(self):
        """Should find page with NFC filename using NFD lookup."""
        # Create page with NFC (composed) characters
        nfc_name = unicodedata.normalize('NFC', "Orontinórë")
        page = Page(
            source_path=Path(f"{nfc_name}.md"),
            slug="orotinore",
            frontmatter={},
            content="",
        )
        store = ContentStore([page])

        # Lookup with NFD (decomposed) version
        nfd_name = unicodedata.normalize('NFD', "Orontinórë")
        result = store.get_by_name(nfd_name)

        assert result is not None
        assert result == page

    def test_unicode_alias_nfc_vs_nfd(self):
        """Should match Unicode aliases regardless of NFC/NFD normalization."""
        nfc_alias = unicodedata.normalize('NFC', "Café")
        page = Page(
            source_path=Path("coffee-shop.md"),
            slug="coffee-shop",
            frontmatter={"aliases": nfc_alias},
            content="",
        )
        store = ContentStore([page])

        # Lookup with NFD version of the alias
        nfd_alias = unicodedata.normalize('NFD', "Café")
        result = store.get_by_name(nfd_alias)

        assert result is not None
        assert result == page

    def test_unicode_alias_list(self):
        """Should handle Unicode characters in alias lists."""
        page = Page(
            source_path=Path("mountain-elves.md"),
            slug="mountain-elves",
            frontmatter={"aliases": ["Orontinórë", "Mountain Elves"]},
            content="",
        )
        store = ContentStore([page])

        # Lookup with NFC
        nfc_name = unicodedata.normalize('NFC', "Orontinórë")
        result = store.get_by_name(nfc_name)
        assert result is not None

        # Lookup with NFD
        nfd_name = unicodedata.normalize('NFD', "Orontinórë")
        result = store.get_by_name(nfd_name)
        assert result is not None

    def test_resolve_link_with_unicode_nfc(self):
        """Should resolve wiki-links with NFC Unicode characters."""
        page = Page(
            source_path=Path("Orontinórë.md"),
            slug="orotinore",
            frontmatter={},
            content="",
        )
        store = ContentStore([page])

        nfc_name = unicodedata.normalize('NFC', "Orontinórë")
        url = store.resolve_link(nfc_name)

        assert url is not None
        assert "/orotinore/" in url

    def test_resolve_link_with_unicode_nfd(self):
        """Should resolve wiki-links with NFD Unicode characters."""
        page = Page(
            source_path=Path("Orontinórë.md"),
            slug="orotinore",
            frontmatter={},
            content="",
        )
        store = ContentStore([page])

        nfd_name = unicodedata.normalize('NFD', "Orontinórë")
        url = store.resolve_link(nfd_name)

        assert url is not None
        assert "/orotinore/" in url

    def test_case_insensitive_with_unicode(self):
        """Should be case-insensitive with Unicode characters."""
        page = Page(
            source_path=Path("Orontinórë.md"),
            slug="orotinore",
            frontmatter={},
            content="",
        )
        store = ContentStore([page])

        # Different case combinations
        assert store.get_by_name("orontinórë") is not None
        assert store.get_by_name("ORONTINÓRË") is not None
        assert store.get_by_name("oRoNtInÓrË") is not None

    def test_multiple_unicode_pages(self):
        """Should handle multiple pages with Unicode filenames."""
        pages = [
            Page(
                source_path=Path("Café.md"),
                slug="cafe",
                frontmatter={},
                content="",
            ),
            Page(
                source_path=Path("Zürich.md"),
                slug="zurich",
                frontmatter={},
                content="",
            ),
            Page(
                source_path=Path("Orontinórë.md"),
                slug="orotinore",
                frontmatter={},
                content="",
            ),
        ]
        store = ContentStore(pages)

        assert store.get_by_name("Café") is not None
        assert store.get_by_name("Zürich") is not None
        assert store.get_by_name("Orontinórë") is not None

    def test_unicode_in_path_components(self):
        """Should handle Unicode in directory paths."""
        page = Page(
            source_path=Path("Groups/Orontinórë.md"),
            slug="groups/orotinore",
            frontmatter={},
            content="",
        )
        store = ContentStore([page])

        # Lookup by just the filename stem
        result = store.get_by_name("Orontinórë")

        assert result is not None
        assert result == page

    def test_various_accented_characters(self):
        """Should handle various accented characters from different languages."""
        test_cases = [
            ("Ñoño.md", "Ñoño"),
            ("Señor.md", "Señor"),
            ("Über.md", "Über"),
            ("Crème.md", "Crème"),
            ("Æther.md", "Æther"),
        ]

        for filename, lookup_name in test_cases:
            page = Page(
                source_path=Path(filename),
                slug="test",
                frontmatter={},
                content="",
            )
            store = ContentStore([page])

            result = store.get_by_name(lookup_name)
            assert result is not None, f"Failed to find {lookup_name}"
