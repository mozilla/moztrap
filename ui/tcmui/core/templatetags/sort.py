from django.template import Library

from .. import sort
from ..util import add_to_querystring



register = Library()



@register.filter
def sort_url(request, field):
    current_field, direction = sort.from_request(request)
    if field == current_field:
        direction = sort.toggle(direction)
    else:
        direction = sort.DEFAULT

    return sort.url(request.get_full_path(), field, direction)
