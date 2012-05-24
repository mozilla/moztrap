"""
Template tags and filters for the finder.

"""
from django.template import Library

from .. import filters



register = Library()



@register.filter
def filter_url(view, obj):
    """Template filter to get filtered url."""
    return filters.filter_url(view, obj)
