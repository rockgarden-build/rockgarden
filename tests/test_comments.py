"""Tests for Obsidian comment stripping (%% comment %%)."""

from rockgarden.obsidian.comments import strip_comments


class TestInlineComments:
    def test_inline_comment_stripped(self):
        result = strip_comments("Hello %% secret %% world")
        assert result == "Hello  world"

    def test_multiple_inline_comments(self):
        result = strip_comments("A %% one %% B %% two %% C")
        assert result == "A  B  C"

    def test_comment_at_start(self):
        result = strip_comments("%% comment %%rest")
        assert result == "rest"

    def test_comment_at_end(self):
        result = strip_comments("content%% comment %%")
        assert result == "content"


class TestBlockComments:
    def test_multiline_comment(self):
        content = "before\n%%\nthis is\na comment\n%%\nafter"
        result = strip_comments(content)
        assert result == "before\n\nafter"

    def test_entire_line_comment(self):
        result = strip_comments("line 1\n%% hidden %%\nline 2")
        assert result == "line 1\n\nline 2"


class TestCodeBlockProtection:
    def test_fenced_code_block_preserved(self):
        content = "```\n%% not a comment %%\n```"
        result = strip_comments(content)
        assert "%% not a comment %%" in result

    def test_inline_code_preserved(self):
        result = strip_comments("Use `%% comment %%` syntax")
        assert "%% comment %%" in result

    def test_tilde_fence_preserved(self):
        content = "~~~\n%% not a comment %%\n~~~"
        result = strip_comments(content)
        assert "%% not a comment %%" in result

    def test_mixed_code_and_comments(self):
        content = "Real %% hidden %% text\n```\n%% kept %%\n```"
        result = strip_comments(content)
        assert "Real" in result
        assert "hidden" not in result
        assert "%% kept %%" in result


class TestEdgeCases:
    def test_no_comments(self):
        result = strip_comments("just normal text")
        assert result == "just normal text"

    def test_single_percent(self):
        result = strip_comments("50% complete")
        assert result == "50% complete"

    def test_empty_comment(self):
        result = strip_comments("before%%%%after")
        assert result == "beforeafter"
