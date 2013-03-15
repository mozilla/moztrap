"""
List pagination utilities.

"""
import math
from django.db.utils import DatabaseError
from ..utils.querystring import update_querystring



PAGESIZES = [10, 20, 50, 100]
DEFAULT_PAGESIZE = 20



def from_request(request):
    """
    Given a request, return tuple (pagesize, pagenumber).

    """
    pagesize = positive_integer(
        request.GET.get("pagesize", DEFAULT_PAGESIZE), DEFAULT_PAGESIZE)
    pagenumber = positive_integer(
        request.GET.get("pagenumber", 1), 1)
    return pagesize, pagenumber



def pagesize_url(url, pagesize):
    return update_querystring(url, pagesize=pagesize, pagenumber=1)



def pagenumber_url(url, pagenumber):
    return update_querystring(url, pagenumber=pagenumber)



class Pager(object):
    """Handles pagination given queryset, page size, and page number."""
    def __init__(self, queryset, pagesize, pagenumber):
        """Initialize a ``Pager`` with queryset, page size, and page number."""
        self._queryset = queryset
        self._sliced_qs = None
        self._cached_total = None
        self.pagesize = pagesize
        self.pagenumber = pagenumber


    def sizes(self):
        """
        Returns an ordered list of pagesize links to display.

        Includes all default page sizes, plus the current page size.

        """
        return sorted(set(PAGESIZES + [self.pagesize]))


    def pages(self):
        """Returns an iterable of valid page numbers."""
        return xrange(1, self.num_pages + 1)


    def display_pages(self):
        """
        Returns an iterable of page numbers to display.

        Elides some ranges of page numbers with None in long lists.

        """
        MIN_SKIP = 3  # don't bother eliding just one or two pages
        FROM_CURRENT = 2  # always show two to either side of current page
        FROM_END = 2  # always show two from each end

        skip = []
        ret = []
        for p in self.pages():
            if (abs(p - self.pagenumber) > FROM_CURRENT and
                p > FROM_END and (self.num_pages - p) > (FROM_END - 1)):
                skip.append(p)
                continue
            if len(skip) < MIN_SKIP:
                ret.extend(skip)
            else:
                ret.append(None)
            ret.append(p)
            skip = []
        return ret


    @property
    def total(self):
        """The total number of objects."""
        if self._cached_total is None:
            # @@@ Django 1.5 should not require the .values part and could be
            # changed to just:
            #     self._cached_total = self._queryset.count()
            # Bug 18248
            try:
                self._cached_total = self._queryset.count()
            except DatabaseError:
                self._cached_total = self._queryset.values("id").count()

        return self._cached_total


    @property
    def objects(self):
        """
        The iterable of objects on the current page.

        Lazily slices the queryset and caches the sliced queryset for
        subsequent access.

        """
        if self._sliced_qs is None:
            if not self.high:
                self._sliced_qs = self._queryset.empty()
            else:
                self._sliced_qs = self._queryset[self.low - 1:self.high]
        return self._sliced_qs


    @property
    def num_pages(self):
        """The total number of pages."""
        return max(1, int(math.ceil(float(self.total) / self.pagesize)))


    @property
    def low(self):
        """Ordinal of the first object on the current page."""
        return self._constrain((self.pagesize * (self.pagenumber - 1)) + 1)


    @property
    def high(self):
        """Ordinal of the last object on the current page."""
        return self._constrain(self.pagesize * self.pagenumber)


    def _constrain(self, num):
        """Return given ``num`` constrained to between 0 and self.total."""
        return min(self.total, max(0, num))


    @property
    def prev(self):
        """Page number of the previous page; None if no previous page."""
        prev = self.pagenumber - 1
        if prev < 1:
            return None
        return prev


    @property
    def next(self):
        """Page number of the next page; None if there is no next page."""
        next = self.pagenumber + 1
        if next > self.num_pages:
            return None
        return next



def positive_integer(val, default):
    """Attempt to coerce ``val`` to a positive integer, with fallback."""
    try:
        val = int(val)
    except (AttributeError, TypeError, ValueError):
        val = default

    if val < 1:
        val = 1

    return val
