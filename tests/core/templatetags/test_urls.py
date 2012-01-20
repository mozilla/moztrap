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
from django.utils.unittest import TestCase

from cc.core.templatetags import urls



class FilterTest(TestCase):
    """Tests for URL-related template filters."""
    def test_is_url(self):
        """is_url filter detects a full URL."""
        self.assertTrue(urls.is_url("http://www.example.com"))


    def test_is_not_url(self):
        """is_url filter detects a non-URL."""
        self.assertFalse(urls.is_url("1234567"))
