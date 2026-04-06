"""Tests for CDN auto-detection (math/mermaid)."""

from rockgarden.config import Config, SiteConfig, ThemeConfig
from rockgarden.output.builder import build_site


def _build_with_content(tmp_path, content, theme_config=None):
    """Build a single-page site and return the output HTML."""
    source = tmp_path / "content"
    source.mkdir()
    (source / "page.md").write_text(content)
    output = tmp_path / "output"
    config = Config(
        site=SiteConfig(source=source, output=output),
        theme=theme_config or ThemeConfig(),
    )
    build_site(config, source, output)
    return (output / "page" / "index.html").read_text()


def test_auto_math_detected(tmp_path):
    html = _build_with_content(tmp_path, "# Math\n\n$x^2$\n")
    assert "katex" in html.lower()


def test_auto_math_not_detected(tmp_path):
    html = _build_with_content(tmp_path, "# No math\n\nJust text.\n")
    assert "katex" not in html.lower()


def test_auto_mermaid_detected(tmp_path):
    html = _build_with_content(
        tmp_path, "# Diagram\n\n```mermaid\ngraph LR\n  A-->B\n```\n"
    )
    assert "mermaid" in html


def test_auto_mermaid_not_detected(tmp_path):
    html = _build_with_content(tmp_path, "# No diagrams\n\nJust text.\n")
    assert "mermaid.esm" not in html


def test_math_cdn_true_always_loads(tmp_path):
    html = _build_with_content(
        tmp_path, "# No math\n\nJust text.\n", ThemeConfig(math_cdn=True)
    )
    assert "katex" in html.lower()


def test_math_cdn_false_never_loads(tmp_path):
    html = _build_with_content(
        tmp_path, "# Math\n\n$x^2$\n", ThemeConfig(math_cdn=False)
    )
    assert "katex" not in html.lower()


def test_mermaid_cdn_true_always_loads(tmp_path):
    html = _build_with_content(
        tmp_path, "# No diagrams\n\nJust text.\n", ThemeConfig(mermaid_cdn=True)
    )
    assert "mermaid.esm" in html


def test_mermaid_cdn_false_never_loads(tmp_path):
    html = _build_with_content(
        tmp_path,
        "# Diagram\n\n```mermaid\ngraph LR\n  A-->B\n```\n",
        ThemeConfig(mermaid_cdn=False),
    )
    assert "mermaid.esm" not in html


def test_math_block_detected(tmp_path):
    html = _build_with_content(tmp_path, "# Math\n\n```math\nx^2\n```\n")
    assert "katex" in html.lower()


def test_config_auto_default():
    config = ThemeConfig()
    assert config.math_cdn == "auto"
    assert config.mermaid_cdn == "auto"


def test_config_invalid_cdn_value():
    import pytest

    with pytest.raises(ValueError, match="must be true, false, or 'auto'"):
        ThemeConfig(math_cdn="always")
