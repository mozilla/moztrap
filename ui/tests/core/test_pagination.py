from mock import Mock
from unittest2 import TestCase



class TestFromRequest(TestCase):
    @property
    def func(self):
        from tcmui.core.pagination import from_request
        return from_request


    def _check(self, GET, result):
        request = Mock()
        request.GET = GET
        self.assertEqual(self.func(request), result)


    def test_defaults(self):
        self._check({}, (20, 1))


    def test_set(self):
        self._check({"pagesize": 10, "pagenumber": 2}, (10, 2))


    def test_invalid(self):
        self._check({"pagesize": "blah", "pagenumber": 2}, (20, 2))


    def test_negative(self):
        self._check({"pagesize": 15, "pagenumber": -2}, (15, 1))



class TestPagesizeUrl(TestCase):
    @property
    def func(self):
        from tcmui.core.pagination import pagesize_url
        return pagesize_url


    def test_simple(self):
        self.assertEqual(
            self.func("http://fake.base/", 10),
            "http://fake.base/?pagenumber=1&pagesize=10")


    def test_override(self):
        self.assertEqual(
            self.func("http://fake.base/?pagesize=40&pagenumber=3", 10),
            "http://fake.base/?pagenumber=1&pagesize=10")



class TestPagenumberUrl(TestCase):
    @property
    def func(self):
        from tcmui.core.pagination import pagenumber_url
        return pagenumber_url


    def test_simple(self):
        self.assertEqual(
            self.func("http://fake.base/", 3),
            "http://fake.base/?pagenumber=3")


    def test_override(self):
        self.assertEqual(
            self.func("http://fake.base/?pagesize=40&pagenumber=3", 5),
            "http://fake.base/?pagenumber=5&pagesize=40")



class TestPager(TestCase):
    @property
    def pager(self):
        from tcmui.core.pagination import Pager
        return Pager


    def test_sizes_with_standard_size(self):
        p = self.pager(5, 10, 1)
        self.assertEqual(p.sizes(), [10, 20, 50, 100])


    def test_sizes_with_nonstandard_size(self):
        p = self.pager(5, 15, 1)
        self.assertEqual(p.sizes(), [10, 15, 20, 50, 100])


    def test_pages_empty(self):
        p = self.pager(0, 20, 1)
        self.assertEqual(list(p.pages()), [1])


    def test_pages_less_than_size(self):
        p = self.pager(10, 20, 1)
        self.assertEqual(list(p.pages()), [1])


    def test_pages_equal_to_size(self):
        p = self.pager(20, 20, 1)
        self.assertEqual(list(p.pages()), [1])


    def test_pages_more_than_size(self):
        p = self.pager(21, 20, 1)
        self.assertEqual(list(p.pages()), [1, 2])


    def test_total_simple(self):
        p = self.pager(10, 20, 1)
        self.assertEqual(p.total, 10)


    def test_total_callable(self):
        p = self.pager(lambda: 5, 20, 1)
        self.assertEqual(p.total, 5)


    def test_total_callable_cached(self):
        t = Mock(return_value=5)
        p = self.pager(t, 20, 1)
        p.total
        p.total
        self.assertEqual(t.call_count, 1)


    def test_num_pages_empty(self):
        self.assertEqual(self.pager(0, 20, 1).num_pages, 1)


    def test_num_pages_less_than_size(self):
        self.assertEqual(self.pager(15, 20, 1).num_pages, 1)


    def test_num_pages_equal_to_size(self):
        self.assertEqual(self.pager(20, 20, 1).num_pages, 1)


    def test_num_pages_more_than_size(self):
        self.assertEqual(self.pager(21, 20, 1).num_pages, 2)


    def test_low_empty(self):
        self.assertEqual(self.pager(0, 20, 1).low, 0)


    def test_high_empty(self):
        self.assertEqual(self.pager(0, 20, 1).high, 0)


    def test_low_less_than_size(self):
        self.assertEqual(self.pager(15, 20, 1).low, 1)


    def test_high_less_than_size(self):
        self.assertEqual(self.pager(15, 20, 1).high, 15)


    def test_low_equal_to_size(self):
        self.assertEqual(self.pager(20, 20, 1).low, 1)


    def test_high_equal_to_size(self):
        self.assertEqual(self.pager(20, 20, 1).high, 20)


    def test_low_more_than_size_page1(self):
        self.assertEqual(self.pager(21, 20, 1).low, 1)


    def test_high_more_than_size_page1(self):
        self.assertEqual(self.pager(21, 20, 1).high, 20)


    def test_low_more_than_size_page2(self):
        self.assertEqual(self.pager(21, 20, 2).low, 21)


    def test_high_more_than_size_page2(self):
        self.assertEqual(self.pager(21, 20, 2).high, 21)


    def test_prev_none(self):
        self.assertEqual(self.pager(5, 20, 1).prev, None)


    def test_prev(self):
        self.assertEqual(self.pager(25, 20, 2).prev, 1)


    def test_next_none(self):
        self.assertEqual(self.pager(5, 20, 1).next, None)


    def test_next(self):
        self.assertEqual(self.pager(25, 20, 1).next, 2)



class TestPositiveInteger(TestCase):
    @property
    def func(self):
        from tcmui.core.pagination import positive_integer
        return positive_integer


    def test_negative(self):
        self.assertEqual(self.func(-1, 5), 1)


    def test_zero(self):
        self.assertEqual(self.func(0, 5), 1)


    def test_positive(self):
        self.assertEqual(self.func(1, 5), 1)


    def test_none(self):
        self.assertEqual(self.func(None, 5), 5)


    def test_string(self):
        self.assertEqual(self.func("blah", 5), 5)
