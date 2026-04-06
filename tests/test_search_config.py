"""Tests for search stopword configuration."""

import pytest

from rockgarden.config import Config, SearchConfig, SiteConfig
from rockgarden.output.builder import build_site


def test_stopwords_default():
    config = SearchConfig()
    assert config.stopwords == "default"


def test_stopwords_none():
    config = SearchConfig(stopwords="none")
    assert config.stopwords == "none"


def test_stopwords_custom_list():
    config = SearchConfig(stopwords=["the", "a", "an"])
    assert config.stopwords == ["the", "a", "an"]


def test_stopwords_invalid_string():
    with pytest.raises(ValueError, match="stopwords must be"):
        SearchConfig(stopwords="custom")


def _build_and_get_html(tmp_path, stopwords="default"):
    source = tmp_path / "content"
    source.mkdir()
    (source / "page.md").write_text("# Hello\n\nSome content.\n")
    output = tmp_path / "output"
    config = Config(
        site=SiteConfig(source=source, output=output),
        search=SearchConfig(stopwords=stopwords),
    )
    build_site(config, source, output)
    return (output / "page" / "index.html").read_text()


def test_default_stopwords_no_pipeline_change(tmp_path):
    html = _build_and_get_html(tmp_path, "default")
    assert "lunr.stopWordFilter" not in html
    assert "generateStopWordFilter" not in html


def test_none_stopwords_removes_filter(tmp_path):
    html = _build_and_get_html(tmp_path, "none")
    assert "this.pipeline.remove(lunr.stopWordFilter)" in html


def test_custom_stopwords_sets_filter(tmp_path):
    html = _build_and_get_html(tmp_path, ["the", "a"])
    assert "generateStopWordFilter" in html
    assert '"the"' in html
    assert '"a"' in html
