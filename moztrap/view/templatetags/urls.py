"""
Template tags/filters related to URL-handling.

"""
from django.conf import settings
from django.template import Library



register = Library()



@register.filter
def is_url(val):
    """Return True if ``val`` appears to be a URL, False otherwise."""
    return "://" in val



@register.simple_tag
def protocol():
    """
    Return 'https' or 'http', depending on the configuration.

    Keys off the ``SESSION_COOKIE_SECURE`` setting, which should be set to True
    for HTTPS deployments.

    """
    return "https" if settings.SESSION_COOKIE_SECURE else "http"
