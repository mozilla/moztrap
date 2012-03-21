# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
#
# This file is part of Case Conductor.
#
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
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
