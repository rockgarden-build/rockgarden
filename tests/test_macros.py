"""Tests for user-defined Jinja2 macros."""

import pytest
from jinja2 import TemplateError

from rockgarden.macros import load_macros, preprocess_macros

# --- load_macros ---


def test_load_macros_missing_dir(tmp_path):
    result = load_macros(tmp_path / "_macros")
    assert result == {}


def test_load_macros_empty_dir(tmp_path):
    (tmp_path / "_macros").mkdir()
    result = load_macros(tmp_path / "_macros")
    assert result == {}


def test_load_macros_loads_html_files(tmp_path):
    macros_dir = tmp_path / "_macros"
    macros_dir.mkdir()
    (macros_dir / "dnd.html").write_text(
        "{% macro stat_block(name) %}<b>{{ name }}</b>{% endmacro %}"
    )
    (macros_dir / "utils.html").write_text(
        "{% macro em(text) %}<em>{{ text }}</em>{% endmacro %}"
    )
    result = load_macros(macros_dir)
    assert set(result.keys()) == {"dnd", "utils"}
    assert "stat_block" in result["dnd"]


def test_load_macros_ignores_non_html(tmp_path):
    macros_dir = tmp_path / "_macros"
    macros_dir.mkdir()
    (macros_dir / "dnd.html").write_text("{% macro foo() %}bar{% endmacro %}")
    (macros_dir / "readme.md").write_text("# readme")
    result = load_macros(macros_dir)
    assert set(result.keys()) == {"dnd"}


# --- preprocess_macros ---


def test_preprocess_macros_no_macros_returns_content():
    content = "Hello {{ world }}"
    result = preprocess_macros(content, {}, None)
    assert result == content


def test_preprocess_macros_basic_macro_call():
    macros = {"greet": "{% macro greet(name) %}Hello, {{ name }}!{% endmacro %}"}
    content = "{{ greet('World') }}"
    result = preprocess_macros(content, macros, None)
    assert result == "Hello, World!"


def test_preprocess_macros_multiple_macro_files():
    macros = {
        "dnd": (
            "{% macro stat_block(name, ac) %}"
            "<b>{{ name }}</b> AC:{{ ac }}{% endmacro %}"
        ),
        "utils": "{% macro em(text) %}<em>{{ text }}</em>{% endmacro %}",
    }
    content = "{{ stat_block('Goblin', 13) }} {{ em('fast') }}"
    result = preprocess_macros(content, macros, None)
    assert "<b>Goblin</b> AC:13" in result
    assert "<em>fast</em>" in result


def test_preprocess_macros_page_context():
    macros = {"meta": "{% macro show_title() %}{{ page.title }}{% endmacro %}"}
    content = "# Page\n{{ show_title() }}"

    class FakePage:
        title = "My Page"

    result = preprocess_macros(content, macros, FakePage())
    assert "My Page" in result


def test_preprocess_macros_passes_page_as_none():
    macros = {"m": "{% macro noop() %}ok{% endmacro %}"}
    result = preprocess_macros("{{ noop() }}", macros, None)
    assert result == "ok"


def test_preprocess_macros_syntax_error_raises():
    macros = {"bad": "{% macro broken( %}{% endmacro %}"}
    with pytest.raises(TemplateError):
        preprocess_macros("{{ broken() }}", macros, None)


def test_preprocess_macros_undefined_variable_raises():
    macros = {"m": "{% macro foo() %}bar{% endmacro %}"}
    with pytest.raises(TemplateError):
        preprocess_macros("{{ undefined_var }}", macros, None)


def test_preprocess_macros_fenced_code_block_preserved():
    macros = {"m": "{% macro foo() %}bar{% endmacro %}"}
    content = "before\n```\n{{ undefined_var }}\n```\nafter"
    result = preprocess_macros(content, macros, None)
    assert "{{ undefined_var }}" in result


def test_preprocess_macros_inline_code_preserved():
    macros = {"m": "{% macro foo() %}bar{% endmacro %}"}
    content = "Use `{{ undefined_var }}` inline"
    result = preprocess_macros(content, macros, None)
    assert "`{{ undefined_var }}`" in result


def test_preprocess_macros_macro_call_outside_fence_still_works():
    macros = {"m": "{% macro greet(name) %}Hi {{ name }}{% endmacro %}"}
    content = "{{ greet('World') }}\n```\n{{ greet('ignored') }}\n```"
    result = preprocess_macros(content, macros, None)
    assert "Hi World" in result
    assert "{{ greet('ignored') }}" in result


def test_preprocess_macros_content_without_calls_unchanged():
    macros = {"m": "{% macro foo() %}bar{% endmacro %}"}
    content = "Just plain markdown content."
    result = preprocess_macros(content, macros, None)
    assert result == "Just plain markdown content."
