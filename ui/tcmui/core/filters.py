from collections import namedtuple



class Filter(object):
    """
    Encapsulates a set of possible filters on a ListObject and their current
    state.

    """
    def __init__(self, GET, **fields):
        """
        ``GET`` is request.GET from the current request.

        Remaining keyword arguments map field names to a FilterField class
        containing the filtering options for that field.

        """
        self.fields = [
            fieldfilter_cls(fieldname, GET.getlist(fieldname))
            for fieldname, fieldfilter_cls in fields.iteritems()
            ]


    def __iter__(self):
        for field in self.fields:
            yield field


    def filter(self, list_obj):
        """
        Return the given ListObject filtered according to the current values of
        our filters.

        """
        filters = dict((field.name, field.values) for field in self.fields)
        return list_obj.filter(**filters)



class FieldFilter(object):
    """
    Encapsulates the state of filtering for a single field.

    Subclasses should define an "options" attribute that is a list of tuples,
    where each tuple consists of a filter value and label for that option.

    """
    def __init__(self, name, current):
        self.name = name
        self.values = set(current)


    options = []


    def __iter__(self):
        for o in self.options:
            yield FilterOption(
                value=o[0], label=o[1], selected=(str(o[0]) in self.values))


    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.name, self.values)



FilterOption = namedtuple("FilterOption", ["value", "label", "selected"])
