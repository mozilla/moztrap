from django.template import Library

from .. import pagination



register = Library()



@register.filter
def pagenumber_url(request, pagenumber):
    return pagination.pagenumber_url(request.get_full_path(), pagenumber)



@register.filter
def pagesize_url(request, pagesize):
    return pagination.pagesize_url(request.get_full_path(), pagesize)
