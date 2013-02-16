"""
Utilities for filtering querysets in a view.

"""

from collections import namedtuple
from functools import wraps
import json
import urlparse

from django.core.urlresolvers import reverse, resolve
from django.utils.datastructures import MultiValueDict

from moztrap.model.core.models import ProductVersion


def filter_url(path_or_view, obj):
    """
    Return URL for ``path_or_view`` filtered by ``obj``.

    ``path_or_view`` should be a URL path, a view function, or a url pattern
    name resolvable without arguments, and ``obj`` should be an instance of a
    model for which there is a ``ModelFilter`` applied to that view.

    For instance, ``filter_url("manage_cases", product)`` would return the URL
    for viewing the manage list of cases, filtered by ``product``.

    """
    if callable(path_or_view):
        view_func = path_or_view
        path = reverse(view_func)
    else:
        if path_or_view.startswith("/"):
            path = path_or_view
        else:
            path = reverse(path_or_view)

        view_func = resolve(path).func

    params = view_func.filterset.params_for(obj)

    return "{0}?{1}".format(
        path,
        "&".join(["{0}={1}".format(k, v) for k, v in params.items()])
        )



def filter(ctx_name, filters=None, filterset_class=None):
    """
    View decorator that handles filtering of a queryset.

    Expects to find the queryset in the TemplateResponse context under the name
    ``ctx_name``. Optional ``filters`` argument should be an iterable of Filter
    instances, and ``filterset_class`` is an optional FilterSet subclass to
    use.

    """
    if filters is None:
        filters = []
    if filterset_class is None:
        filterset_class = FilterSet
    filterset = filterset_class(filters)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            try:
                ctx = response.context_data
            except AttributeError:
                return response
            bfs = filterset.bind(request.GET, request.COOKIES)
            ctx[ctx_name] = bfs.filter(ctx[ctx_name])
            ctx["filters"] = bfs
            return response

        # annotate wrapped view with filterset
        # for introspection by e.g. filter_url
        _wrapped_view.filterset = filterset

        return _wrapped_view

    return decorator



class BoundFilterSet(object):
    """A FilterSet plus actual filtering data."""
    def __init__(self, filterset, data=None):
        """
        Initialize a BoundFilterSet.

        ``filterset`` is the FilterSet instance that provides the filters;
        ``data`` is a dictionary mapping filter keys to lists of values.

        """
        self.data = data or {}
        self.filterset = filterset
        self.filters = self.filterset.filters
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



class PinnedFilters(object):
    """An object to manage pinned filters saved as cookies in the session."""

    def __init__(self, COOKIES):
        self.cookie_prefix = "moztrap-filter-"
        self.cookies = {}
        if COOKIES:
            for k in COOKIES.keys():
                if k.startswith(self.cookie_prefix):
                    filter_key = k[len(self.cookie_prefix):]
                    pinned_filters = json.loads(
                        urlparse.unquote(COOKIES.get(k)))
                    self.cookies[filter_key] = pinned_filters


    def extend_filters(self, filters):
        # pinned filters are stored in session cookies.  Add them to the list
        # of other filters in the querystring.
        for k, v in self.cookies.items():
            filters.setdefault(k, []).extend(v)
        return filters


    def fill_form_querystring(self, GET):
        # pinned filters are stored in session cookies.  Fill in, if not
        # already set.  Don't want to overwrite or add to existing values
        # and only if there's a single matching cookie value
        new_filters = GET.copy()
        for k, v in self.cookies.items():
            if not k in new_filters and len(v) == 1:
                new_filters[k] = v[0]
        return new_filters



class FilterSet(object):
    """A set of possible filters on a queryset."""
    # subclasses can have preset filters
    filters = []

    bound_class = BoundFilterSet


    def __init__(self, filters=None, prefix="filter-"):
        """
        Initialize a FilterSet.

        ``filters`` is an optional iterable of additional Filter instances.

        """
        if filters:
            self.filters = self.filters[:]
            self.filters.extend(filters)
        self.prefix = prefix


    def bind(self, GET=None, COOKIES=None):
        """
        Return BoundFilterSet (or subclass) for given filter data.

         ``GET`` is a MultiValueDict that may contain filtering keys; usually
        request.GET from the current request. Keys not beginning with
        ``self.prefix``` will be ignored.

        """
        GET = GET or MultiValueDict()

        query_filters = dict(
            (k[len(self.prefix):], GET.getlist(k)) for k in GET.keys()
            if k.startswith(self.prefix)
            )

        # pinned filters are stored in session cookies.  Add them to the list
        # of other filters in the querystring.
        if COOKIES:
            PinnedFilters(COOKIES).extend_filters(query_filters)

        return self.bound_class(
            self,
            query_filters,
            )


    def __iter__(self):
        """Iteration yields filters."""
        return iter(self.filters)


    def params_for(self, obj):
        """
        Return dict; querystring parameters to filter for ``obj``.

        Only useful if filterset contains a ModelFilter for ``obj``'s class,
        otherwise will return empty dict.

        """
        for flt in self.filters:
            qs = getattr(flt, "queryset", None)
            if qs is not None:
                if isinstance(obj, qs.model):
                    return {"{0}{1}".format(self.prefix, flt.key): obj.pk}

        return {}



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
        return iter(self.options)


    def __len__(self):
        return len(self.options)



class Filter(object):
    """Encapsulates the filtering possibilities for a single field."""
    # A filter-type class; for use in CSS styling of the filter input
    cls = ""


    def __init__(self, name, lookup=None, key=None, coerce=None,
        extra_filters=None):
        """
        Instantiate the Filter.

        ``name`` is the public name of the filter, ``lookup`` is the field used
        for filtering a queryset, and ``key`` is the key under which data for
        this filter is found in the provided filter data. Both ``lookup`` and
        ``key`` default to ``name`` if not provided. ``coerce`` is a
        one-argument function to coerce values to the correct type for this
        filter; it may raise ValueError or TypeError.
        ``extra_filters`` is a dict containing any extra filters that should be
        attached to this filter.  For example, you might want to add
        ``is_latest`` to a ``result status`` filter.

        """
        self.name = name
        self.lookup = name if lookup is None else lookup
        self.key = name if key is None else key
        self.extra_filters = {} if extra_filters is None else extra_filters
        self._coerce_func = coerce


    def filter(self, queryset, values):
        """Given queryset and selected values, return filtered queryset."""
        if values:
            filters = {"{0}__in".format(self.lookup): values}
            filters.update(self.extra_filters)
            return queryset.filter(
                **filters).distinct()
        return queryset


    def options(self, values):
        """Given list of selected values, return options to display."""
        return []


    def values(self, data):
        """Given data dict, return list of selected values."""
        return [v for v in map(self.coerce, data.get(self.key, []))]


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
