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
Tests for pagination utilities.

"""
from mock import Mock
from django.test import TestCase

from ... import factories as F
from ...utils import Url



class TestFromRequest(TestCase):
    """Tests for ``from_request`` function."""
    @property
    def func(self):
        """The function under test."""
        from cc.view.lists.pagination import from_request
        return from_request


    def _check(self, GET, result):
        """Assert that a request with ``GET`` params gives ``result``"""
        request = Mock()
        request.GET = GET
        self.assertEqual(self.func(request), result)


    def test_defaults(self):
        """Defaults to page 1, 20 per page, if no values in querystring."""
        self._check({}, (20, 1))


    def test_set(self):
        """Values from querystring override defaults."""
        self._check({"pagesize": 10, "pagenumber": 2}, (10, 2))


    def test_invalid(self):
        """Non-numbers fallback to default."""
        self._check({"pagesize": "blah", "pagenumber": 2}, (20, 2))


    def test_negative(self):
        """Out-of-bounds numbers are constrained to bounds."""
        self._check({"pagesize": 15, "pagenumber": -2}, (15, 1))



class TestPagesizeUrl(TestCase):
    """Tests for ``pagesize_url`` function."""
    @property
    def func(self):
        """The function under test."""
        from cc.view.lists.pagination import pagesize_url
        return pagesize_url


    def test_simple(self):
        """Adds pagenumber and pagesize to a URL with neither in querystring."""
        self.assertEqual(
            Url(self.func("http://fake.base/", 10)),
            Url("http://fake.base/?pagenumber=1&pagesize=10"))


    def test_override(self):
        """Overrides existing values in querystring, jumping back to page 1."""
        self.assertEqual(
            Url(self.func("http://fake.base/?pagesize=40&pagenumber=3", 10)),
            Url("http://fake.base/?pagenumber=1&pagesize=10"))



class TestPagenumberUrl(TestCase):
    """Tests for ``pagenumber_url`` function."""
    @property
    def func(self):
        """The function under test."""
        from cc.view.lists.pagination import pagenumber_url
        return pagenumber_url


    def test_simple(self):
        """Adds pagenumber to a URL without it in querystring."""
        self.assertEqual(
            Url(self.func("http://fake.base/", 3)),
            Url("http://fake.base/?pagenumber=3"))


    def test_override(self):
        """Overrides existing value in querystring."""
        self.assertEqual(
            Url(self.func("http://fake.base/?pagesize=40&pagenumber=3", 5)),
            Url("http://fake.base/?pagenumber=5&pagesize=40"))



class TestPager(TestCase):
    """Tests for ``Pager`` class."""
    @property
    def pager(self):
        """The class under test."""
        from cc.view.lists.pagination import Pager
        return Pager


    def qs(self, count):
        """Returns mock queryset with given count."""
        qs = Mock()
        qs.count.return_value = count
        qs.__getitem__ = Mock()
        return qs


    def test_sizes_with_standard_size(self):
        """Has built-in standard set of page-size options."""
        p = self.pager(self.qs(5), 10, 1)
        self.assertEqual(p.sizes(), [10, 20, 50, 100])


    def test_sizes_with_nonstandard_size(self):
        """Current pagesize is always included in page-size options."""
        p = self.pager(self.qs(5), 15, 1)
        self.assertEqual(p.sizes(), [10, 15, 20, 50, 100])


    def test_pages_empty(self):
        """With no objects, there's still one page."""
        p = self.pager(self.qs(0), 20, 1)
        self.assertEqual(list(p.pages()), [1])


    def test_pages_less_than_size(self):
        """With fewer objects than one full page, there's one page."""
        p = self.pager(self.qs(10), 20, 1)
        self.assertEqual(list(p.pages()), [1])


    def test_pages_equal_to_size(self):
        """With exactly one page's worth of objects, there's one page."""
        p = self.pager(self.qs(20), 20, 1)
        self.assertEqual(list(p.pages()), [1])


    def test_pages_more_than_size(self):
        """With more than one page's worth of objects, there's two pages."""
        p = self.pager(self.qs(21), 20, 1)
        self.assertEqual(list(p.pages()), [1, 2])


    def test_display_pages_empty(self):
        """With no objects, one page is linked in nav."""
        p = self.pager(self.qs(0), 20, 1)
        self.assertEqual(list(p.display_pages()), [1])


    def test_display_pages_less_than_size(self):
        """With less than one page's objects, one page is linked in nav."""
        p = self.pager(self.qs(10), 20, 1)
        self.assertEqual(list(p.display_pages()), [1])


    def test_display_pages_equal_to_size(self):
        """With exactly one page's objects, one page is linked in nav."""
        p = self.pager(self.qs(20), 20, 1)
        self.assertEqual(list(p.display_pages()), [1])


    def test_display_pages_more_than_size(self):
        """With more than one page's objects, both pages are linked in nav."""
        p = self.pager(self.qs(21), 20, 1)
        self.assertEqual(list(p.display_pages()), [1, 2])


    def test_display_pages_long_on_first(self):
        """With many pages, some in the middle are elided."""
        p = self.pager(self.qs(120), 10, 1)
        self.assertEqual(list(p.display_pages()), [1, 2, 3, None, 11, 12])


    def test_display_pages_long_on_last(self):
        """At least two pages on each side of current page are shown."""
        p = self.pager(self.qs(120), 10, 12)
        self.assertEqual(list(p.display_pages()), [1, 2, None, 10, 11, 12])


    def test_display_pages_long_near_one_end(self):
        """If only one page would be elided, it isn't."""
        p = self.pager(self.qs(120), 10, 5)
        self.assertEqual(
        list(p.display_pages()), [1, 2, 3, 4, 5, 6, 7, None, 11, 12])


    def test_display_pages_long_near_other_end(self):
        """Overlap between near-current and near-end is not a problem."""
        p = self.pager(self.qs(120), 10, 9)
        self.assertEqual(
            list(p.display_pages()), [1, 2, None, 7, 8, 9, 10, 11, 12])


    def test_display_pages_long_in_middle(self):
        """May be two elisions, if in middle of long page set."""
        p = self.pager(self.qs(150), 10, 8)
        self.assertEqual(list(p.display_pages()), [1, 2, None, 6, 7, 8, 9, 10, None, 14, 15])


    def test_total(self):
        """Total number of objects is count of queryset."""
        p = self.pager(self.qs(10), 20, 1)
        self.assertEqual(p.total, 10)


    def test_total_cached(self):
        """Checking total twice doesn't query db for count twice."""
        qs = self.qs(10)
        p = self.pager(qs, 20, 1)

        p.total
        p.total

        self.assertEqual(qs.count.call_count, 1)


    def test_objects(self):
        """.objects is list of objects on current page."""
        products = [
            F.ProductFactory.create(name="Product {0}".format(i))
            for i in range(1, 5)
            ]
        p = self.pager(products[0].__class__.objects.all(), 3, 1)

        self.assertEqual(list(p.objects), products[:3])


    def test_sliced_queryset_cached(self):
        """Accessing .objects twice does not query db twice."""
        qs = self.qs(10)
        p = self.pager(qs, 5, 1)

        p.objects
        p.objects

        self.assertEqual(qs.__getitem__.call_count, 1)


    def test_num_pages_empty(self):
        """With no objects, there's still one page."""
        self.assertEqual(self.pager(self.qs(0), 20, 1).num_pages, 1)


    def test_num_pages_less_than_size(self):
        """With less than one page's objects, there's one page."""
        self.assertEqual(self.pager(self.qs(15), 20, 1).num_pages, 1)


    def test_num_pages_equal_to_size(self):
        """With exactly one page's objects, there's one page."""
        self.assertEqual(self.pager(self.qs(20), 20, 1).num_pages, 1)


    def test_num_pages_more_than_size(self):
        """With more than one page's objects, there's one page."""
        self.assertEqual(self.pager(self.qs(21), 20, 1).num_pages, 2)


    def test_low_empty(self):
        """With no objects, the first displayed is the zero-th."""
        self.assertEqual(self.pager(self.qs(0), 20, 1).low, 0)


    def test_high_empty(self):
        """With no objects, the last displayed is the zero-th."""
        self.assertEqual(self.pager(self.qs(0), 20, 1).high, 0)


    def test_low_less_than_size(self):
        """With only one page, the first displayed is the first."""
        self.assertEqual(self.pager(self.qs(15), 20, 1).low, 1)


    def test_high_less_than_size(self):
        """With only one page, the last displayed is the last."""
        self.assertEqual(self.pager(self.qs(15), 20, 1).high, 15)


    def test_low_equal_to_size(self):
        """With exactly one page's objects, first displayed is the first."""
        self.assertEqual(self.pager(self.qs(20), 20, 1).low, 1)


    def test_high_equal_to_size(self):
        """With exactly one page's objects, last displayed is the last."""
        self.assertEqual(self.pager(self.qs(20), 20, 1).high, 20)


    def test_low_more_than_size_page1(self):
        """With more than one page, first on first page is the first."""
        self.assertEqual(self.pager(self.qs(21), 20, 1).low, 1)


    def test_high_more_than_size_page1(self):
        """With more than one page, last on first page is the page size-th."""
        self.assertEqual(self.pager(self.qs(21), 20, 1).high, 20)


    def test_low_more_than_size_page2(self):
        """With two pages, first on second page is page-size+1-th."""
        self.assertEqual(self.pager(self.qs(21), 20, 2).low, 21)


    def test_high_more_than_size_page2(self):
        """With two pages, last on second page is the last."""
        self.assertEqual(self.pager(self.qs(21), 20, 2).high, 21)


    def test_prev_none(self):
        """If there is no previous page, .prev is None."""
        self.assertEqual(self.pager(self.qs(5), 20, 1).prev, None)


    def test_prev(self):
        "If there is a previous page, .prev is its number."""
        self.assertEqual(self.pager(self.qs(25), 20, 2).prev, 1)


    def test_next_none(self):
        """If there is no next page, .next is None."""
        self.assertEqual(self.pager(self.qs(5), 20, 1).next, None)


    def test_next(self):
        """If there is a next page, .next is its number."""
        self.assertEqual(self.pager(self.qs(25), 20, 1).next, 2)



class TestPositiveInteger(TestCase):
    """Tests for ``positive_integer`` function."""
    @property
    def func(self):
        """The function under test."""
        from cc.view.lists.pagination import positive_integer
        return positive_integer


    def test_negative(self):
        """Negative numbers are coerced to 1."""
        self.assertEqual(self.func(-1, 5), 1)


    def test_zero(self):
        """Zero is coerced to 1."""
        self.assertEqual(self.func(0, 5), 1)


    def test_positive(self):
        """Positive in-bounds numbers are returned as-is."""
        self.assertEqual(self.func(1, 5), 1)


    def test_none(self):
        """None is coerced to the given default."""
        self.assertEqual(self.func(None, 5), 5)


    def test_string(self):
        """Non-numbers are coerced to the given default."""
        self.assertEqual(self.func("blah", 5), 5)
