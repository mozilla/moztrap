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



def filter(ctx_name, filters=None, filterset=None):
    """
    View decorator that handles filtering of a queryset.

    Expects to find the queryset in the TemplateResponse context under the name
    ``ctx_name``. Optional ``filters`` argument should be an iterable of Filter
    instances, and ``filterset`` is an optional FilterSet subclass to use.

    """
    if filters is None:
        filters = []
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
            fs = filterset(request.GET, filters)
            ctx[ctx_name] = fs.filter(ctx[ctx_name])
            ctx["filters"] = fs
            return response

        return _wrapped_view

    return decorator



class FilterSet(object):
    """A set of possible filters on a queryset and their current state."""
    # subclasses can have preset filters
    filters = []


    def __init__(self, GET, filters=None, prefix="filter-"):
        """
        Initialize a FilterSet.

        ``GET`` is a MultiValueDict that may contain filtering keys; usually
        request.GET from the current request. Keys not beginning with
        ``prefix``` will be ignored.

        ``filters`` is an optional iterable of additional Filter instances.

        """
        self.data = dict(
            (k[len(prefix):], GET.getlist(k)) for k in GET.keys()
            if k.startswith(prefix)
            )
        if filters:
            self.filters = self.filters[:]
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
    """A Filter plus specific filtering values from the request."""
    def __init__(self, flt, data):
        """``flt`` is a Filter instance, ``data`` is a dict of filter data."""
        self._filter = flt
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


    def __init__(self, name, lookup=None, key=None, coerce=None):
        """
        Instantiate the Filter.

        ``name`` is the public name of the filter, ``lookup`` is the field used
        for filtering a queryset, and ``key`` is the key under which data for
        this filter is found in the provided filter data. Both ``lookup`` and
        ``key`` default to ``name`` if not provided. ``coerce`` is a
        one-argument function to coerce values to the correct type for this
        filter; it may raise ValueError or TypeError.

        """
        self.name = name
        self.lookup = name if lookup is None else lookup
        self.key = name if key is None else key
        self._coerce_func = coerce


    def filter(self, queryset, values):
        """Given queryset and selected values, return filtered queryset."""
        if values:
            return queryset.filter(
                **{"{0}__in".format(self.lookup): values}).distinct()
        return queryset


    def options(self, values):
        """Given list of selected values, return options to display."""
        return []


    def values(self, data):
        """Given data dict, return list of selected values."""
        return [
            v for v in map(self.coerce, data.get(self.key, []))
            if v is not None
            ]


    def coerce(self, value):
        """
        Coerce a string value to the value type of this Filter's options.

        For instance, a related-field-lookup filter might have integer object
        IDs as option values, and would coerce all incoming filter values to
        integers.

        Should return None if a value cannot be coerced.
        """
        if self._coerce_func is None:
            return value
        try:
            return self._coerce_func(value)
        except (ValueError, TypeError):
            return None



class BaseChoicesFilter(Filter):
    """A Filter with a fixed set of choices."""
    def get_choices(self):
        """Return this filter's choices, a list of (value, label) tuples."""
        return []


    def options(self, values):
        """Given list of selected values, return options to display."""
        return self.get_choices()


    def values(self, data):
        """Given data dict, return list of selected values."""
        choice_values = set([k for k, v in self.get_choices()])
        return [
            v for v in
            super(BaseChoicesFilter, self).values(data)
            if v is not None and v in choice_values
            ]



class ChoicesFilter(BaseChoicesFilter):
    """A filter whose choices are passed in at instantiation."""
    def __init__(self, *args, **kwargs):
        """Looks for ``choices`` kwarg."""
        choices = kwargs.pop("choices")
        super(ChoicesFilter, self).__init__(*args, **kwargs)
        self._choices = choices


    def get_choices(self):
        """Return the passed-in choices."""
        return self._choices



class ModelFilter(BaseChoicesFilter):
    """
    A Filter whose choices are from a provided iterable of model instances.

    By default, assumes the model has a numeric primary key; if not an
    alternative ``coerce`` function should be provided at instantiation.

    """
    def __init__(self, *args, **kwargs):
        """
        Looks for ``queryset`` and ``label`` keyword arguments.

        ``queryset`` should contain the model instances that are the options
        available for this filter; ``label`` is an optional one-argument
        callable that returns the display label for each object, given the
        object.

        """
        self.queryset = kwargs.pop("queryset")
        self.label_func = kwargs.pop("label", lambda o: unicode(o))
        kwargs.setdefault("coerce", int)
        super(ModelFilter, self).__init__(*args, **kwargs)


    def get_choices(self):
        """Get the options for this filter."""
        # always clone to get new data; filter instances are persistent
        return [(obj.pk, self.label_func(obj)) for obj in self.queryset.all()]



class KeywordExactFilter(Filter):
    """Allows user to input arbitrary filter values; no pre-set options list."""
    cls = "keyword"


    def options(self, values):
        """Options displayed are always the current filter values."""
        return [(v, v) for v in values]



class KeywordFilter(KeywordExactFilter):
    """Values are ANDed in a 'contains' search of the field"""


    def filter(self, queryset, values):
        """Values are ANDed in a 'contains' search of the field text."""
        for value in values:
            queryset = queryset.filter(
                **{"{0}__icontains".format(self.lookup): value})

        if values:
            return queryset.distinct()

        return queryset
