"""
Template tags for pagination.

"""
from django.template import Library

from classytags.core import Tag, Options
from classytags.arguments import Argument

from .. import pagination



register = Library()



class Paginate(Tag):
    """Paginate the given queryset, placing a Pager in the template context."""
    name = "paginate"
    options = Options(
        Argument("queryset"),
        "as",
        Argument("varname", resolve=False),
        )


    def render_tag(self, context, queryset, varname):
        """Place Pager for given ``queryset`` in context as ``varname``."""
        request = context["request"]
        pagesize, pagenum = pagination.from_request(request)
        context[varname] = pagination.Pager(queryset, pagesize, pagenum)
        return u""


register.tag(Paginate)



@register.filter
def pagenumber_url(request, pagenumber):
    """Return current full URL with pagenumber replaced."""
    return pagination.pagenumber_url(request.get_full_path(), pagenumber)



@register.filter
def pagesize_url(request, pagesize):
    """Return current full URL with pagesize replaced."""
    return pagination.pagesize_url(request.get_full_path(), pagesize)


@register.filter
def pagenumber(request):
    """Return pagenumber of given request."""
    return pagination.from_request(request)[1]


@register.filter
def pagesize(request):
    """Return pagesize of given request."""
    return pagination.from_request(request)[0]
