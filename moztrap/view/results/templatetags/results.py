"""
Results-viewing template tags and filters.

"""
import math

from django import template



register = template.Library()



@register.filter
def percentage(val):
    """
    Convert a real number between 0 and 1 to a percentage from 0 to 100.

    Rounds up when under 0.5/50% and down when over. This ensures that the
    endpoints are special; we never call anything "0%" or "100%" unless it
    really is exactly that.

    """
    val = val * 100
    if val > 50:
        val = math.floor(val)
    else:
        val = math.ceil(val)
    return int(val)
