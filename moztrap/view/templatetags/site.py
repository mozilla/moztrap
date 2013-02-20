"""Template tags/filters for site-level pages."""
from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def settings_value(name):
    """Return the requested setting value and place it in context under ``varname``"""
    return getattr(settings, name, "")
