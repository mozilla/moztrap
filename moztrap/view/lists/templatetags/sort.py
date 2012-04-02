"""
Template tags/filters for sorting.

"""
from django.template import Library



register = Library()



@register.filter
def url(sort, field):
    return sort.url(field)



@register.filter
def dir(sort, field):
    return sort.dir(field)
