"""
Tests for URL-related template filters.

"""
from django.template import Template, Context

# @@@ import from Django in 1.4
from djangosecure.test_utils import override_settings

from tests import case



class FilterTest(case.TestCase):
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



class ProtocolTest(case.TestCase):
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
