"""
Open Web App template tags and filters.

"""
from django import template
from django.core.urlresolvers import reverse



register = template.Library()



@register.filter
def owa_manifest_url(request):
    """Return the full absolute url for the open web app manifest."""
    return request.build_absolute_uri(reverse("owa_manifest"))
