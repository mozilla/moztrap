"""
Utilities for views that sort list of objects.

"""
from functools import wraps

from django.core.exceptions import FieldError

from ..utils.querystring import update_querystring



DIRECTIONS = set(["asc", "desc"])
DEFAULT = "asc"



def sort(ctx_name, defaultfield=None, defaultdirection=DEFAULT):
    """Sort queryset found in TemplateResponse context under ``ctx_name``."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            try:
                ctx = response.context_data
            except AttributeError:
                return response
            ctx["sort"] = Sort(request, defaultfield, defaultdirection)
            try:
                sortqs = ctx[ctx_name].order_by(*ctx["sort"].order_by)
                str(sortqs.query)  # hack to force evaluation of sort arguments
            except FieldError:
                pass
            else:
                ctx[ctx_name] = sortqs
            return response

        return _wrapped_view

    return decorator



class Sort(object):
    def __init__(self, request, defaultfield=None, defaultdirection=DEFAULT):
        """
        Accepts request, looks for GET keys "sortfield" and "sortdirection".

        A "field" can actually be multiple field names concatenated with
        commas, in which case all of those fields will be sorted on, in
        descending priority order.

        """
        self.url_path = request.get_full_path()
        self.field = request.GET.get("sortfield", defaultfield)
        self.direction = request.GET.get("sortdirection", defaultdirection)
        if self.field is None:
            self.field = "created_on"
            self.direction = "desc"


    def url(self, field):
        """
        Return a url for switching the sort to the given field name.

        """
        direction = DEFAULT
        if field == self.field:
            direction = DIRECTIONS.difference([self.direction]).pop()
        return update_querystring(
            self.url_path, sortfield=field, sortdirection=direction)


    def dir(self, field):
        """
        Return the current sort direction for the given field.

        asc, desc, or empty string if this isn't the field sorted on currently.

        """
        if field == self.field:
            return self.direction
        return ""


    @property
    def order_by(self):
        """Return the ``order_by`` tuple appropriate for this sort."""
        fields = self.field.split(",")
        if self.direction == "desc":
            return tuple(["-" + f for f in fields])
        return tuple(fields)
