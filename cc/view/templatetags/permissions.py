"""
Permission-related tags and filters.

"""
from django import template



register = template.Library()



@register.filter
def has_perm(user, perm):
    """Return True if the user has the given permission, false otherwise."""
    return user.has_perm(perm)
