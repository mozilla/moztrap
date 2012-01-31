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
Template tags and filters for the finder.

"""
from django.template import Library



register = Library()



@register.filter
def child_query_url(finder, obj):
    """Return Ajax query URL for children of given object."""
    return finder.child_query_url(obj)


@register.filter
def sub_name(finder, obj):
    """Return name of child column of this object."""
    return finder.child_column_for_obj(obj)


@register.filter
def goto_url(finder, obj):
    """Return "goto" url for this object."""
    return finder.goto_url(obj)
