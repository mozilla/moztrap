"""
Template tags and filters for the finder.

"""

import json

from django.template import Library
from django import template

from .. import filters



register = Library()



@register.filter
def filter_url(view, obj):
    """Template filter to get filtered url."""
    return filters.filter_url(view, obj)
