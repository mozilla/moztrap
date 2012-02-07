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
from django.template import Template, Context
from django.utils.unittest import TestCase

# @@@ import from Django in 1.4
from djangosecure.test_utils import override_settings



class FilterTest(TestCase):
    """Tests for URL-related template filters."""
    @property
    def urls(self):
        """The templatetag module under test."""
        from cc.view.templatetags import urls
        return urls


    def test_is_url(self):
        """is_url filter detects a full URL."""
        self.assertTrue(self.urls.is_url("http://www.example.com"))


    def test_is_not_url(self):
        """is_url filter detects a non-URL."""
        self.assertFalse(self.urls.is_url("1234567"))



class ProtocolTest(TestCase):
    """Tests for the protocol template tag."""
    def tag(self):
        """Return the output of the {% protocol %} template tag."""
        t = Template("{% load urls %}{% protocol %}")
        return t.render(Context({}))


    @override_settings(SESSION_COOKIE_SECURE=False)
    def test_http(self):
        """protocol tag returns 'http' if SESSION_COOKIE_SECURE is False."""
        self.assertEqual(self.tag(), "http")


    @override_settings(SESSION_COOKIE_SECURE=True)
    def test_https(self):
        """protocol tag returns 'https' if SESSION_COOKIE_SECURE is True."""
        self.assertEqual(self.tag(), "https")
