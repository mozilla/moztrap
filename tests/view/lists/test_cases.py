"""
Tests for queryset-filtering.

"""
from mock import Mock

from django.template.response import TemplateResponse
from django.test import RequestFactory
from django.utils.datastructures import MultiValueDict

from tests import case



class CaseFiltersTestCase(case.TestCase):
    """A test case for testing classes in the moztrap.view.lists.filters module."""
    @property
    def filters(self):
        """The module under test."""
        from moztrap.view.lists import cases
        return cases



class KeywordFilterTest(FiltersTestCase):
    """Tests for KeywordFilter."""
    def test_filter(self):
        """Filters queryset by 'contains' all values."""
        f = self.filters.KeywordFilter("name")

        qs = Mock()
        qs2 = f.filter(qs, ["one", "two"])

        qs.filter.assert_called_with(name__icontains="one")
        qs.filter.return_value.filter.assert_called_with(name__icontains="two")
        qs.filter.return_value.filter.return_value.distinct.assert_called_with()
        self.assertIs(
            qs2,
            qs.filter.return_value.filter.return_value.distinct.return_value)


    def test_filter_doesnt_touch_queryset_if_no_values(self):
        """Doesn't call .distinct() or .filter() unless actually filtered."""
        f = self.filters.KeywordFilter("name")

        qs = Mock()
        f.filter(qs, [])

        self.assertEqual(qs.filter.call_count, 0)
        self.assertEqual(qs.distinct.call_count, 0)

class PrefixIDFilterTest(FiltersTestCase):
    """
    prefix and ID
    prefix only
    ID only
    id when case has no prefix
    2 cases have 2 different prefixes OR'ed
    2 cases with no prefixes, IDs OR'ed


    """