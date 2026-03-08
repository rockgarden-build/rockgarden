"""Tests for icon access from Jinja2 templates."""

import logging

from markupsafe import Markup

from rockgarden.config import Config
from rockgarden.render.engine import _icon, create_engine


def _render(template_str: str) -> str:
    config = Config()
    env = create_engine(config)
    return env.from_string(template_str).render()


class TestIconInTemplates:
    def test_icon_global_renders_svg(self):
        html = _render('{{ icon("lucide:info") }}')
        assert "<svg" in html

    def test_icon_filter_renders_svg(self):
        html = _render('{{ "lucide:info" | icon }}')
        assert "<svg" in html

    def test_icon_unqualified_defaults_to_lucide(self):
        qualified = _render('{{ icon("lucide:info") }}')
        unqualified = _render('{{ icon("info") }}')
        assert qualified == unqualified
        assert "<svg" in unqualified

    def test_icon_missing_returns_empty(self):
        html = _render('{{ icon("lucide:nonexistent-zzz") }}')
        assert html == ""

    def test_icon_missing_logs_warning(self, caplog):
        with caplog.at_level(logging.WARNING, logger="rockgarden.render.engine"):
            _render('{{ icon("lucide:nonexistent-zzz") }}')
        assert "nonexistent-zzz" in caplog.text

    def test_icon_output_is_markup(self):
        result = _icon("lucide:info")
        assert isinstance(result, Markup)
        assert "<svg" in result

    def test_icon_missing_output_is_markup(self):
        result = _icon("lucide:nonexistent-zzz")
        assert isinstance(result, Markup)
        assert result == ""
