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
Tests for sort template filters.

"""
from mock import Mock

from django.utils.unittest import TestCase

from cc.core.templatetags import sort



class FilterTest(TestCase):
    """Tests for sort template filters."""
    def test_url(self):
        """url filter passes through to url method of Sort object."""
        s = Mock()

        sort.url(s, "name")

        s.url.assert_called_with("name")


    def test_dir(self):
        """dir filter passes through to dir method of Sort object."""
        s = Mock()

        sort.dir(s, "name")

        s.dir.assert_called_with("name")
