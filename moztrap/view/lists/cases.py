from filters import KeywordFilter
from django.db.models import Q

class PrefixIDFilter(KeywordFilter):
    """
    A string and an int, separated by a delimiter.
    Values are split by the right-most occurrence of delimiter and ANDed
    across prefix and ID.  Must match exactly the prefix or the ID, or both, if
    both are provided.

    if more than one of these filters is used, they are ORed with each other.
    """


    def __init__(self, name, delimiter="-"):
        self.prefixlookup = "case__idprefix"
        self.delimiter = delimiter
        super(PrefixIDFilter, self).__init__(name, lookup="case__id")


    def filter(self, queryset, values):

        query_filters = Q()

        for value in values:

            # split the prefix from the id
            prefix, sep, caseid = value.rpartition(self.delimiter)

            # if there is a prefix of abc-xyz, then we don't want to
            # try searching in the int field for xyz, presume it's all
            # the prefix, as the suffix MUST always be numeric.
            # also, if the user put the delimiter at the end, strip it off
            if not caseid.isdecimal():
                prefix = value.rstrip(self.delimiter)
                caseid = None

            kwargs = {}

            if prefix:
                kwargs["{0}__exact".format(self.prefixlookup)] = prefix
            if caseid:
                kwargs["{0}__exact".format(self.lookup)] = caseid

            query_filters = query_filters | Q(**kwargs)

        if values:
            return queryset.filter(query_filters).distinct()

        return queryset
