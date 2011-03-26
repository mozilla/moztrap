import math

from .util import add_to_querystring



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
    return add_to_querystring(url, pagesize=pagesize, pagenumber=1)



def pagenumber_url(url, pagenumber):
    return add_to_querystring(url, pagenumber=pagenumber)



class Paginator(object):
    def __init__(self, total, pagesize, pagenumber):
        self.total = total
        self.pagesize = pagesize
        self.pagenumber = pagenumber


    def sizes(self):
        return sorted(set(PAGESIZES + [self.pagesize]))


    def pages(self):
        return xrange(1, self.num_pages + 1)


    @property
    def num_pages(self):
        return int(math.ceil(float(self.total) / self.pagesize))


    @property
    def low(self):
        return max(0, (self.pagesize * (self.pagenumber - 1)) + 1)


    @property
    def high(self):
        return min(self.total, (self.pagesize * self.pagenumber))


    @property
    def prev(self):
        prev = self.pagenumber - 1
        if prev < 1:
            return None
        return prev


    @property
    def next(self):
        next = self.pagenumber + 1
        if next > self.num_pages:
            return None
        return next



def positive_integer(val, default):
    try:
        val = int(val)
    except AttributeError:
        val = default

    if val < 1:
        val = 1

    return val
