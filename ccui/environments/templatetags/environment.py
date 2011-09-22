from django import template
from django.core.urlresolvers import reverse

from classytags.core import Tag, Options
from classytags.arguments import Argument

from ..forms import EnvironmentSelectionForm



register = template.Library()



class GetEnvironmentSelectionForm(Tag):
    name = "get_environment_selection_form"
    options = Options(
        "for",
        Argument("environmentgroups"),
        "as",
        Argument("varname", resolve=False)
        )


    def render_tag(self, context, environmentgroups, varname):
        request = context["request"]
        context[varname] = EnvironmentSelectionForm(
            groups=environmentgroups,
            current=request.session.get("environments", None))
        return u""


register.tag(GetEnvironmentSelectionForm)



@register.filter
def set_environment_url(run):
    return reverse("runtests_environment", kwargs={"testrun_id": run.id})
