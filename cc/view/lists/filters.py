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
Utilities for filtering querysets in a view.

"""
from collections import namedtuple
from functools import wraps



def filter(ctx_name, filterset=None, *filters):
    """
    View decorator that handles filtering of a queryset.

    Expects to find the queryset in the TemplateResponse context under the name
    ``ctx_name``. Each additional argument should be a Filter instance.

    """
    if filterset is None:
        filterset = FilterSet
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            try:
                ctx = response.context_data
            except AttributeError:
                return response
            fs = filterset(filters, request.GET)
            ctx[ctx_name] = fs.filter(ctx[ctx_name])
            ctx["filters"] = fs
            return response

        return _wrapped_view

    return decorator



class FilterSet(object):
    """A set of possible filters on a queryset and their current state."""
    # subclasses can have preset filters
    filters = []


    def __init__(self, filters, GET, prefix="filter-"):
        """
        Initialize a FilterSet.

        ``GET`` is a MultiValueDict containing filtering keys; usually
        request.GET from the current request. Keys not beginning with
        ``prefix``` will be ignored.

        ``filters`` is an iterable of Filter instances.

        """
        self.data = dict(
            (k[len(prefix):], GET.getlist(k)) for k in GET.keys()
            if k.startswith(prefix)
            )
        if filters:
            self.filters.extend(filters)
        self.boundfilters = [BoundFilter(f, self.data) for f in self.filters]


    def __iter__(self):
        """Iteration yields BoundFilters."""
        for f in self.boundfilters:
            yield f


    def __len__(self):
        """Length is number of member filters."""
        return len(self.boundfilters)


    def filter(self, queryset):
        """Return ``queryset`` filtered by current values of our filters."""
        for boundfilter in self.boundfilters:
            queryset = boundfilter.filter(queryset)
        return queryset



FilterOption = namedtuple("FilterOption", ["value", "label", "selected"])



class BoundFilter(object):
    """A Filter plus specific filtering values."""
    def __init__(self, filter, data):
        """``flt`` is a Filter instance, ``data`` is a dict of filter data."""
        self._filter = filter
        self.data = data

        # list of valid selected option values
        self.values = self._filter.values(self.data)

        value_set = set(self.values)
        self.options = [
            FilterOption(
                value=val, label=label, selected=(val in value_set))
            for val, label in self._filter.options(self.values)]


    def filter(self, queryset):
        """Return filtered queryset."""
        return self._filter.filter(queryset, self.values)


    @property
    def cls(self):
        """Pass-through to Filter cls."""
        return self._filter.cls


    @property
    def name(self):
        """Pass-through to Filter name."""
        return self._filter.name


    @property
    def key(self):
        """Pass-through to Filter key."""
        return self._filter.key


    def __iter__(self):
        """Yields FilterOption objects when iterated."""
        for o in self.options:
            yield o


    def __len__(self):
        return len(self.options)



class Filter(object):
    """Encapsulates the filtering possibilities for a single field."""
    # A filter-type class; for use in CSS styling of the filter input
    cls = ""


    def __init__(self, name, lookup=None, key=None):
        """
        Instantiate the Filter.

        ``name`` is the public name of the filter, ``lookup`` is the field used
        for filtering a queryset, and ``key`` is the key under which data for
        this filter is found in the provided filter data. Both ``lookup`` and
        ``key`` default to ``name`` if not provided.

        """
        self.name = name
        self.lookup = name if lookup is None else lookup
        self.key = name if key is None else key


    def filter(self, queryset, values):
        """Given queryset and selected values, return filtered queryset."""
        return queryset


    def options(self, values):
        """Given list of selected values, return options to display."""
        return []


    def values(self, data):
        """Given data dict, return list of selected values."""
        return data.get(self.key, [])



class BaseChoicesFilter(Filter):
    """A Filter with a fixed set of choices."""
    def __init__(self, *args, **kwargs):
        """Initialize a BaseChoicesFilter."""
        self._cached_choices = None
        super(BaseChoicesFilter, self).__init__(*args, **kwargs)


    @property
    def choices(self):
        """Property proxy for get_choices; ensures it is called only once."""
        if self._cached_choices is None:
            self._cached_choices = self.get_choices()
        return self._cached_choices


    def get_choices(self):
        """
        Return this filter's choices, a list of (value, label) tuples.

        Subclasses should override, and don't need to worry about caching the
        results; this function will only be called once per page load.

        """
        return []


    def filter(self, queryset, values):
        """Given queryset and selected values, return filtered queryset."""
        if values:
            return queryset.filter(**{"{0}__in".format(self.lookup): values})
        return queryset


    def options(self, values):
        """Given list of selected values, return options to display."""
        return self.choices


    def values(self, data):
        """Given data dict, return list of selected values."""
        choice_values = set([k for k, v in self.choices])
        return [
            v for v in
            map(self.coerce, super(BaseChoicesFilter, self).values(data))
            if v is not None and v in choice_values
            ]


    def coerce(self, value):
        """
        Coerce a string value to the value type of this Filter's options.

        For instance, a related-field-lookup filter might have integer object
        IDs as option values, and would coerce all incoming filter values to
        integers.

        Should return None if a value cannot be coerced.

        """
        return value



class ChoicesFilter(BaseChoicesFilter):
    """A filter whose choices are passed in at instantiation."""
    def __init__(self, *args, **kwargs):
        """Looks for ``choices`` kwarg."""
        choices = kwargs.pop("choices")
        super(ChoicesFilter, self).__init__(*args, **kwargs)
        self._cached_choices = choices



class RelatedFieldFilter(BaseChoicesFilter):
    """
    A Filter for related fields.

    Gets its choices from a provided queryset. Assumes the queryset model has a
    numeric "id" primary key.

    """
    def __init__(self, *args, **kwargs):
        """
        Looks for queryset and label keyword arguments.

        The objects in ``queryset`` are the options available for this filter;
        ``label`` is an optional one-argument function that returns the display
        label for each object, given the object.

        """
        self.queryset = kwargs.pop("queryset")
        self.label_func = kwargs.pop("label", lambda o: unicode(o))
        super(RelatedFieldFilter, self).__init__(*args, **kwargs)


    def get_choices(self):
        """Get the options for this filter."""
        # always clone to get new data; filter instances are persistent
        return [(obj.id, self.label_func(obj)) for obj in self.queryset]


    def coerce(self, value):
        """Attempt to coerce all values to integers."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return None



class KeywordFilter(Filter):
    """Filters by arbitrary keywords rather than a pre-set list of options."""
    cls = "keyword"


    def options(self, values):
        return [(v, v) for v in values]


    def filter(self, queryset, values):
        for value in values:
            queryset = queryset.filter(
                **{"{0}__contains".format(self.lookup): value})

        return queryset
