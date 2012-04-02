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
