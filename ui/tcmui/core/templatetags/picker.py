from django.core.urlresolvers import reverse
from django.template import Library

from ...products.models import Product
from ...testexecution.models import TestCycle, TestRun



register = Library()



URLS = {
    "runtests": {
        Product: "runtests_picker_cycles",
        TestCycle: "runtests_picker_runs",
        TestRun: "runtests_picker_environments",
        }
    }



@register.filter
def picker_sub_url(obj, picker_type):
    try:
        url_pattern = URLS[picker_type][obj.__class__]
    except KeyError:
        return ""
    return reverse(url_pattern, kwargs={"parent_id": obj.id})
