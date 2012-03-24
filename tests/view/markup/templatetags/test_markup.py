"""
Tests for URL-related template filters.

"""
from django.utils.safestring import SafeData

from tests import case



class FilterTest(case.TestCase):
    """Tests for markup-related template filters."""
    @property
    def markup(self):
        """The templatetag module under test."""
        from cc.view.markup.templatetags import markup
        return markup


    def test_markdown_renders_html(self):
        """Markdown filter renders markdown to HTML."""
        self.assertEqual(
            self.markup.markdown("_foo_"), "<p><em>foo</em></p>\n")


    def test_markdown_returns_safestring(self):
        """Markdown filter returns marked-safe HTML string."""
        self.assertIsInstance(self.markup.markdown("_foo"), SafeData)


    def test_markdown_escapes_html(self):
        """Markdown filter escapes HTML."""
        self.assertEqual(
            self.markup.markdown("<script>"), "<p>&lt;script&gt;</p>\n")
