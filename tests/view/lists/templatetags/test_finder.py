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
