"""Tests for GFM task list rendering."""

from rockgarden.render.markdown import render_markdown


class TestTaskLists:
    def test_unchecked_item(self):
        html = render_markdown("- [ ] todo\n")
        assert "task-list-item-checkbox" in html
        assert 'type="checkbox"' in html
        assert "checked" not in html
        assert "todo" in html

    def test_checked_item(self):
        html = render_markdown("- [x] done\n")
        assert 'checked="checked"' in html
        assert "done" in html

    def test_mixed_list(self):
        md = "- [ ] first\n- [x] second\n- [ ] third\n"
        html = render_markdown(md)
        assert html.count('<li class="task-list-item">') == 3
        assert html.count('checked="checked"') == 1

    def test_task_list_classes(self):
        html = render_markdown("- [ ] item\n")
        assert "contains-task-list" in html
        assert "task-list-item" in html

    def test_nested_task_list(self):
        md = "- [ ] parent\n  - [x] child\n"
        html = render_markdown(md)
        assert html.count('<li class="task-list-item">') == 2

    def test_regular_list_not_affected(self):
        html = render_markdown("- normal item\n")
        assert "task-list-item" not in html
