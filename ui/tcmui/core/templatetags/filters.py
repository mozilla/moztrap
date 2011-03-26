from django.template import Library

from classytags.core import Tag, Options
from classytags.arguments import Argument

from .. import filters



register = Library()



@register.filter
def filter_fields(list_obj, cs_fieldnames):
    return filters.filter_fields(
        list_obj,
        *[s.strip() for s in cs_fieldnames.split(",")])



@register.filter
def cancel_filter_url(request, field):
    current_url = request.get_full_path()
    new_url = filters.filter_url(current_url, field)
    if new_url == current_url:
        return None
    return new_url



class FilterUrl(Tag):
    name = "filter_url"
    options = Options(
        Argument("request"),
        Argument("field"),
        Argument("value"),
        "as",
        Argument("as_var", resolve=False)
        )

    def render_tag(self, context, request, field, value, as_var):
        current_url = request.get_full_path()
        new_url = filters.filter_url(current_url, field, value)
        if new_url == current_url:
            new_url = None
        context[as_var] = new_url
        return ""

register.tag(FilterUrl)
