from collections import namedtuple



class Filter(object):
    """
    Encapsulates a set of possible filters on a ListObject and their current
    state.

    """
    def __init__(self, GET, auth, *fields):
        """
        ``GET`` is request.GET from the current request.

        ``auth`` is a Credentials object, if needed for fetching dynamic filter
        options.

        Remaining keyword arguments map field names to a FilterField class
        containing the filtering options for that field.

        """
        self.fields = [
            fieldfilter_cls(fieldname, GET.getlist(fieldname), auth)
            for fieldname, fieldfilter_cls in fields
            ]


    def __iter__(self):
        for field in self.fields:
            yield field


    def filter(self, list_obj):
        """
        Return the given ListObject filtered according to the current values of
        our filters.

        """
        filters = dict(
            field.filters() for field in self.fields if field.include)
        return list_obj.filter(**filters)



FilterOption = namedtuple("FilterOption", ["value", "label", "selected"])



class FieldFilter(object):
    """
    Encapsulates the state of filtering for a single field.

    Subclasses should define an "options" attribute that is a list of tuples,
    where each tuple consists of a filter value and label for that option.

    """
    cls = ""


    def __init__(self, name, values, auth=None):
        self.name = name
        self.values = values
        self.auth = auth


    options = []


    def get_options(self):
        return self.options


    def filters(self):
        """
        Return tuple of (fieldname, values) to filter the API query on.

        """
        return (self.name, self.values)


    @property
    def include(self):
        """
        True if this filter has data and should be included.

        """
        return bool(self.values)


    def __iter__(self):
        for o in self.get_options():
            yield FilterOption(
                value=o[0], label=o[1], selected=(str(o[0]) in self.values))


    def __len__(self):
        return len(self.get_options())


    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.name, self.values)



class RelatedFieldFilter(FieldFilter):
    """
    A FieldFilter for Locator fields and many-to-many fields (e.g. team
    members, environments); gets its options by querying a ListObject subclass
    set as the ``target`` attribute by subclasses, possibly filtered by any
    given ``target_filters``.

    """
    target = None
    target_filters = None


    def target_label(self, x):
        return str(x)


    def get_options(self):
        if not hasattr(self, "_cached_options"):
            lst = self.target.get(auth=self.auth)
            if self.target_filters is not None:
                lst = lst.filter(**self.target_filters)
            self._cached_options = [
                (obj.id, self.target_label(obj)) for obj in lst]
        return self._cached_options



class KeywordFilter(FieldFilter):
    """
    For filtering based on arbitrary keywords entered in the text box, rather
    than a pre-set list of options.

    """
    cls = "keyword"


    def to_platform(self, text):
        if text.startswith("^"):
            text = text[1:]
        else:
            text = "%" + text
        if text.endswith("$"):
            text = text[:-1]
        else:
            text = text + "%"
        return text.replace("*", "%")


    def get_options(self):
        return [(v, v) for v in self.values]


    def filters(self):
        return (self.name, [self.to_platform(v) for v in self.values])
