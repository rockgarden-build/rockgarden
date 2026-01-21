"""Strip leading H1 from markdown content."""

import re

H1_PATTERN = re.compile(
    r"^"  # Start of string
    r"(?:\s*\n)*"  # Optional leading whitespace/newlines
    r"#\s+[^\n]+"  # H1: # followed by space and text
    r"\n?"  # Optional trailing newline
)


def strip_content_title(content: str) -> str:
    """Remove the first H1 heading from markdown content.

    Args:
        content: Markdown content that may start with an H1.

    Returns:
        Content with leading H1 removed (if present).
    """
    return H1_PATTERN.sub("", content, count=1)
