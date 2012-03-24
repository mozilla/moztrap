"""
Tests for sort template filters.

"""
from mock import Mock

from tests import case



class FilterTest(case.TestCase):
    """Tests for sort template filters."""
    @property
    def sort(self):
        """The templatetag module under test."""
        from cc.view.lists.templatetags import sort
        return sort


    def test_url(self):
        """url filter passes through to url method of Sort object."""
        s = Mock()

        ret = self.sort.url(s, "name")

        s.url.assert_called_with("name")
        self.assertIs(ret, s.url.return_value)


    def test_dir(self):
        """dir filter passes through to dir method of Sort object."""
        s = Mock()

        ret = self.sort.dir(s, "name")

        s.dir.assert_called_with("name")
        self.assertIs(ret, s.dir.return_value)
