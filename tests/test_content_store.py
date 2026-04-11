"""Tests for ContentStore link resolution."""

from pathlib import Path

from rockgarden.content.models import Page
from rockgarden.content.store import ContentStore


class TestResolveLink:
    """Test ContentStore.resolve_link() method."""

    def test_basic_page_link(self):
        """Should resolve a basic page link."""
        page = Page(
            source_path=Path("Getting Started.md"),
            slug="getting-started",
            frontmatter={},
            content="",
        )
        store = ContentStore([page])

        url = store.resolve_link("Getting Started")
        assert url == "/getting-started/"

    def test_page_link_with_alias(self):
        """Should resolve link using page alias."""
        page = Page(
            source_path=Path("guide.md"),
            slug="guide",
            frontmatter={"aliases": "Getting Started"},
            content="",
        )
        store = ContentStore([page])

        url = store.resolve_link("Getting Started")
        assert url == "/guide/"

    def test_section_link(self):
        """Should resolve link with section fragment."""
        page = Page(
            source_path=Path("Chamber of the Stone.md"),
            slug="chamber-of-the-stone",
            frontmatter={},
            content="",
        )
        store = ContentStore([page])

        url = store.resolve_link("Chamber of the Stone#Thalador")
        assert url == "/chamber-of-the-stone/#thalador"

    def test_section_link_with_spaces(self):
        """Should preserve spaces in section fragment."""
        page = Page(
            source_path=Path("Session Log.md"),
            slug="session-log",
            frontmatter={},
            content="",
        )
        store = ContentStore([page])

        url = store.resolve_link("Session Log#Group Vision")
        assert url == "/session-log/#group-vision"

    def test_section_link_whitespace_trimmed(self):
        """Should trim whitespace around page name and fragment."""
        page = Page(
            source_path=Path("Notes.md"),
            slug="notes",
            frontmatter={},
            content="",
        )
        store = ContentStore([page])

        url = store.resolve_link("Notes  #  Section  ")
        assert url == "/notes/#section"

    def test_broken_link_returns_none(self):
        """Should return None for non-existent page."""
        store = ContentStore([])

        url = store.resolve_link("Non-Existent Page")
        assert url is None

    def test_broken_section_link_returns_none(self):
        """Should return None for section link to non-existent page."""
        store = ContentStore([])

        url = store.resolve_link("Non-Existent Page#Section")
        assert url is None


class TestMediaFileLinks:
    """Test ContentStore resolution of media file links."""

    def test_image_link_png(self):
        """Should resolve PNG image link."""
        media_index = {
            "calladain.png": ["attachments/CallaDain.png"],
        }
        store = ContentStore([], media_index=media_index)

        url = store.resolve_link("CallaDain.png")
        assert url == "/attachments/CallaDain.png"

    def test_image_link_jpg(self):
        """Should resolve JPG image link."""
        media_index = {
            "photo.jpg": ["images/photo.jpg"],
        }
        store = ContentStore([], media_index=media_index)

        url = store.resolve_link("photo.jpg")
        assert url == "/images/photo.jpg"

    def test_audio_link(self):
        """Should resolve audio file link."""
        media_index = {
            "song.mp3": ["audio/song.mp3"],
        }
        store = ContentStore([], media_index=media_index)

        url = store.resolve_link("song.mp3")
        assert url == "/audio/song.mp3"

    def test_video_link(self):
        """Should resolve video file link."""
        media_index = {
            "video.mp4": ["videos/video.mp4"],
        }
        store = ContentStore([], media_index=media_index)

        url = store.resolve_link("video.mp4")
        assert url == "/videos/video.mp4"

    def test_pdf_link(self):
        """Should resolve PDF file link."""
        media_index = {
            "document.pdf": ["docs/document.pdf"],
        }
        store = ContentStore([], media_index=media_index)

        url = store.resolve_link("document.pdf")
        assert url == "/docs/document.pdf"

    def test_media_link_with_path(self):
        """Should resolve media link with path prefix."""
        media_index = {
            "image.png": ["attachments/images/image.png"],
        }
        store = ContentStore([], media_index=media_index)

        # Obsidian uses filename-only matching
        url = store.resolve_link("attachments/images/image.png")
        assert url == "/attachments/images/image.png"

    def test_missing_media_file(self):
        """Should return None for non-existent media file."""
        media_index = {}
        store = ContentStore([], media_index=media_index)

        url = store.resolve_link("missing.png")
        assert url is None

    def test_page_link_preferred_over_media(self):
        """Should prefer page link over media file when both exist."""
        page = Page(
            source_path=Path("image.md"),
            slug="image",
            frontmatter={},
            content="",
        )
        media_index = {
            "image.md": ["attachments/image.md"],
        }
        store = ContentStore([page], media_index=media_index)

        # Should resolve to page, not media file
        url = store.resolve_link("image")
        assert url == "/image/"

    def test_media_file_with_section(self):
        """Should handle media file link with fragment (unlikely but possible)."""
        media_index = {
            "document.pdf": ["docs/document.pdf"],
        }
        store = ContentStore([], media_index=media_index)

        url = store.resolve_link("document.pdf#page=5")
        assert url == "/docs/document.pdf#page=5"


class TestCleanUrls:
    """Test link resolution with clean_urls setting."""

    def test_clean_urls_enabled(self):
        """Should generate clean URLs when enabled (default)."""
        page = Page(
            source_path=Path("about.md"),
            slug="about",
            frontmatter={},
            content="",
        )
        store = ContentStore([page], clean_urls=True)

        url = store.resolve_link("about")
        assert url == "/about/"

    def test_clean_urls_disabled(self):
        """Should generate .html URLs when disabled."""
        page = Page(
            source_path=Path("about.md"),
            slug="about",
            frontmatter={},
            content="",
        )
        store = ContentStore([page], clean_urls=False)

        url = store.resolve_link("about")
        assert url == "/about.html"

    def test_section_link_clean_urls_disabled(self):
        """Should preserve section fragment with .html URLs."""
        page = Page(
            source_path=Path("notes.md"),
            slug="notes",
            frontmatter={},
            content="",
        )
        store = ContentStore([page], clean_urls=False)

        url = store.resolve_link("notes#section")
        assert url == "/notes.html#section"


class TestFolderNoteResolution:
    """Test wiki-link resolution for folder notes and index pages."""

    def test_index_md_resolves_by_folder_name(self):
        """[[Fairshore]] should resolve to Fairshore/index.md via fallback."""
        page = Page(
            source_path=Path("Fairshore/index.md"),
            slug="fairshore/index",
            frontmatter={},
            content="",
        )
        store = ContentStore([page])

        url = store.resolve_link("Fairshore")
        assert url == "/fairshore/"

    def test_index_fallback_no_overwrite(self):
        """Stem-based match takes priority over index fallback."""
        explicit_page = Page(
            source_path=Path("Fairshore.md"),
            slug="fairshore",
            frontmatter={},
            content="",
        )
        index_page = Page(
            source_path=Path("other/fairshore/index.md"),
            slug="other/fairshore/index",
            frontmatter={},
            content="",
        )
        store = ContentStore([explicit_page, index_page])

        url = store.resolve_link("Fairshore")
        assert url == "/fairshore/"

    def test_folder_note_resolves_by_name(self):
        """Folder note with rewritten slug still resolves via source_path stem."""
        page = Page(
            source_path=Path("locations/Fairshore/Fairshore.md"),
            slug="locations/fairshore/index",
            frontmatter={},
            content="",
        )
        store = ContentStore([page])

        url = store.resolve_link("Fairshore")
        assert url == "/locations/fairshore/"

    def test_index_fallback_case_insensitive(self):
        """Index fallback should be case-insensitive."""
        page = Page(
            source_path=Path("Fairshore/index.md"),
            slug="fairshore/index",
            frontmatter={},
            content="",
        )
        store = ContentStore([page])

        assert store.resolve_link("fairshore") == "/fairshore/"
        assert store.resolve_link("FAIRSHORE") == "/fairshore/"
