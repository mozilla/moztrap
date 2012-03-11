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
Tests for finder template filters.

"""
from mock import Mock

from tests import case



class FilterTest(case.TestCase):
    """Tests for finder template filters."""
    @property
    def finder(self):
        """The templatetag module under test."""
        from cc.view.lists.templatetags import finder
        return finder


    def test_child_query_url(self):
        """child_query_url passes through to method of Filter object."""
        f, o = Mock(), Mock()

        url = self.finder.child_query_url(f, o)

        f.child_query_url.assert_called_with(o)
        self.assertIs(url, f.child_query_url.return_value)


    def test_sub_name(self):
        """sub_name passes through to Filter.child_column_for_obj method."""
        f, o = Mock(), Mock()

        url = self.finder.sub_name(f, o)

        f.child_column_for_obj.assert_called_with(o)
        self.assertIs(url, f.child_column_for_obj.return_value)


    def test_goto_url(self):
        """goto_url passes through to method of Filter object."""
        f, o = Mock(), Mock()

        url = self.finder.goto_url(f, o)

        f.goto_url.assert_called_with(o)
        self.assertIs(url, f.goto_url.return_value)
