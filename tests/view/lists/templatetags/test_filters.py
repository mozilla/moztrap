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
