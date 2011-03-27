from collections import defaultdict, namedtuple

from .util import add_to_querystring



def filter(list_obj, request):
    """
    Given a ListObject and a request, return a clone of that ListObject,
    filtered according to valid filters present in the request.

    """
    fields = list_obj.filterable_fields().keys()
    filters = dict((k, v) for (k, v) in request.GET.iteritems()
                   if k in fields)
    return list_obj.filter(**filters)



def filter_url(url, field, value=None):
    return add_to_querystring(url, **{field: value, "pagenumber": 1})



def filter_fields(list_obj, *args):
    filterable = list_obj.filterable_fields()
    valid_fields = set(filterable.keys())
    fieldnames = [f for f in args if f in valid_fields]
    ffields = dict(
        (fname, (filterable[fname], FilterField(fname)))
        for fname in fieldnames)

    for obj in list_obj:
        for fname, (field, ffield) in ffields.iteritems():
            val = getattr(obj, fname)
            ffield.add((str(val), field.encode(val)))

    return sorted(
        (i[1] for i in ffields.itervalues()),
        key=lambda ff: fieldnames.index(ff.name))



FilterOption = namedtuple("FilterOption", ["name", "value", "count"])


class FilterField(object):
    def __init__(self, name):
        self.name = name
        self._options = defaultdict(lambda: 0)


    def add(self, option):
        self._options[option] += 1


    @property
    def options(self):
        return sorted(
            [FilterOption(name=o[0], value=o[1], count=c)
             for (o, c) in self._options.iteritems()],
            key=lambda fo: fo.count, reverse=True)


    def __repr__(self):
        return "<FilterField: %r %r>" % (self.title, self.options)
