import math

from .util import update_querystring



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
    """
    Given a total number of objects and a current page size and page number,
    can calculate various bits of data handy for displaying pagination
    controls.

    """
    def __init__(self, total, pagesize, pagenumber):
        """
        The ``total`` argument can either be an integer, or a callable that
        when called returns an integer (this is to allow for lazy total
        calculation in cases when the Pager is constructed before the list of
        results is fully ready.)

        """
        self._total = total
        self._cached_total = None
        self.pagesize = pagesize
        self.pagenumber = pagenumber


    def sizes(self):
        """
        Returns an ordered list of pagesize links to display. Includes all
        default page sizes, plus the current page size.

        """
        return sorted(set(PAGESIZES + [self.pagesize]))


    def pages(self):
        """
        Returns an iterable of valid page numbers.

        """
        return xrange(1, self.num_pages + 1)


    def display_pages(self):
        """
        Returns an iterable of page numbers to display, eliding some ranges of
        page numbers with None in long lists.

        """
        MIN_SKIP = 3 # don't bother eliding just one or two pages
        FROM_CURRENT = 2 # always show two to either side of current page
        FROM_END = 2 # always show two from each end

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
        """
        The total number of objects. Handles calling the callable that may have
        been passed in initially, and caching that result so the callable is
        only called once.

        """
        if self._cached_total is None:
            if callable(self._total):
                self._cached_total = self._total()
            else:
                self._cached_total = self._total
        return self._cached_total


    @property
    def num_pages(self):
        """
        Returns the total number of pages.

        """
        return max(1, int(math.ceil(float(self.total) / self.pagesize)))


    @property
    def low(self):
        """
        Returns the ordinal of the first object to be displayed on the current
        page.

        """
        return self._constrain((self.pagesize * (self.pagenumber - 1)) + 1)


    @property
    def high(self):
        """
        Returns the ordinal of the last object to be displayed on the current
        page.

        """
        return self._constrain(self.pagesize * self.pagenumber)


    def _constrain(self, num):
        return min(self.total, max(0, num))


    @property
    def prev(self):
        """
        The page number of the previous page, or None if there is no previous
        page.

        """
        prev = self.pagenumber - 1
        if prev < 1:
            return None
        return prev


    @property
    def next(self):
        """
        The page number of the next page, or None if there is no next page.

        """
        next = self.pagenumber + 1
        if next > self.num_pages:
            return None
        return next



def positive_integer(val, default):
    try:
        val = int(val)
    except (AttributeError, TypeError, ValueError):
        val = default

    if val < 1:
        val = 1

    return val
