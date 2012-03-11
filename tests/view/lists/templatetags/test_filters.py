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
Tests for queryset-filtering.

"""
from django.template import Template, Context

from mock import patch

from tests import case



class FilterUrlTest(case.TestCase):
    """Tests for filter_url template filter."""
    @patch("cc.view.lists.filters.filter_url")
    def test_pass_through(self, mock_filter_url):
        """filter_url template filter is pass-through to filter_url function."""
        t = Template("{% load filters %}{{ 'manage_cases'|filter_url:prod }}")
        product = object()
        mock_filter_url.return_value = "some url"
        res = t.render(Context({"prod": product}))

        self.assertEqual(res, "some url")
        mock_filter_url.assert_called_with("manage_cases", product)
