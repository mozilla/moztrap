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
Utilities for views that sort list of objects.

"""
from functools import wraps

from .querystring import update_querystring



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
            ctx[ctx_name] = ctx[ctx_name].order_by(ctx["sort"].order_by)
            return response

        return _wrapped_view

    return decorator



class Sort(object):
    def __init__(self, request, defaultfield=None, defaultdirection=DEFAULT):
        """
        Accepts the current request.

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
        """Return the ``order_by`` clause appropriate for this sort."""
        if self.direction == "desc":
            return "-" + self.field
        return self.field
