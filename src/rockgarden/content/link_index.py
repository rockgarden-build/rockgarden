"""Link index for tracking wiki-link relationships."""

import re
from dataclasses import dataclass, field

from rockgarden.content.models import Page
from rockgarden.content.store import ContentStore

WIKILINK_PATTERN = re.compile(
    r"\[\["
    r"([^\]|]+)"  # Target (required)
    r"(?:\|[^\]]+)?"  # Display text (optional, after |) - ignored for indexing
    r"\]\]"
)

CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```|`[^`\n]+`")


@dataclass
class LinkIndex:
    """Bidirectional index of wiki-link relationships.

    Tracks both outgoing links (what a page links to) and incoming links
    (what pages link to a page, i.e., backlinks).
    """

    outgoing: dict[str, set[str]] = field(default_factory=dict)
    incoming: dict[str, set[str]] = field(default_factory=dict)

    def get_backlinks(self, slug: str) -> set[str]:
        """Get all pages that link to the given page.

        Args:
            slug: The page slug to get backlinks for.

        Returns:
            Set of page slugs that link to this page.
        """
        return self.incoming.get(slug, set())

    def get_outgoing_links(self, slug: str) -> set[str]:
        """Get all pages that the given page links to.

        Args:
            slug: The page slug to get outgoing links for.

        Returns:
            Set of page slugs this page links to.
        """
        return self.outgoing.get(slug, set())


def extract_wikilink_targets(content: str) -> list[str]:
    """Extract all wiki-link targets from content.

    Ignores wiki-links inside code blocks.

    Args:
        content: Markdown content to extract links from.

    Returns:
        List of link targets (the part inside [[target]]).
    """
    code_blocks: list[str] = []

    def save_code_block(match: re.Match) -> str:
        code_blocks.append(match.group(0))
        return f"\x00CODE{len(code_blocks) - 1}\x00"

    content = CODE_BLOCK_PATTERN.sub(save_code_block, content)

    targets = []
    for match in WIKILINK_PATTERN.finditer(content):
        target = match.group(1).strip()
        targets.append(target)

    return targets


def build_link_index(pages: list[Page], store: ContentStore) -> LinkIndex:
    """Build a bidirectional link index from all pages.

    Extracts wiki-links from each page, resolves them through the store,
    and builds both outgoing and incoming link indexes.

    Args:
        pages: List of all pages in the site.
        store: ContentStore for resolving link targets.

    Returns:
        LinkIndex with bidirectional link relationships.
    """
    index = LinkIndex()

    for page in pages:
        targets = extract_wikilink_targets(page.content)

        for target in targets:
            # Resolve target to a page
            linked_page = store.get_by_name(target)
            if linked_page:
                # Track outgoing link
                if page.slug not in index.outgoing:
                    index.outgoing[page.slug] = set()
                index.outgoing[page.slug].add(linked_page.slug)

                # Track incoming link (backlink)
                if linked_page.slug not in index.incoming:
                    index.incoming[linked_page.slug] = set()
                index.incoming[linked_page.slug].add(page.slug)

    return index
