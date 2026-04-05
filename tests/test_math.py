"""Tests for math rendering support."""

from rockgarden.render.markdown import render_markdown


class TestInlineMath:
    def test_single_dollar(self):
        result = render_markdown("Hello $x^2$ world")
        assert '<span class="math inline">' in result
        assert "x^2" in result

    def test_inline_math_in_sentence(self):
        result = render_markdown("The formula $E = mc^2$ is famous.")
        assert '<span class="math inline">' in result
        assert "E = mc^2" in result

    def test_dollar_in_code_not_math(self):
        result = render_markdown("Use `$variable` in bash")
        assert "math" not in result

    def test_currency_not_math(self):
        result = render_markdown("It costs $50 to $100")
        assert "math" not in result
        assert "$50" in result
        assert "$100" in result

    def test_spaced_dollars_not_math(self):
        result = render_markdown("$ a $")
        assert "math" not in result


class TestBlockMath:
    def test_double_dollar(self):
        result = render_markdown("$$\n\\sum_{i=1}^n x_i\n$$")
        assert '<div class="math block">' in result
        assert "\\sum_{i=1}^n x_i" in result

    def test_math_fence(self):
        result = render_markdown("```math\n\\int_0^1 f(x) dx\n```")
        assert '<div class="math block">' in result
        assert "\\int_0^1 f(x) dx" in result

    def test_non_math_fence_unchanged(self):
        result = render_markdown("```python\nprint('hello')\n```")
        assert "math" not in result
        assert "highlight" in result
