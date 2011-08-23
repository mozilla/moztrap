from django import template

from classytags.core import Tag, Options
from classytags.arguments import Argument

from .. import util
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
def set_environment_url(environmentgroups):
    return util.set_environment_url(environmentgroups)



class MatchEnvironment(Tag):
    name = "match_environment"
    options = Options(
        Argument("items"),
        Argument("environments"),
        "as",
        Argument("varname", resolve=False)
        )


    def render_tag(self, context, items, environments, varname):
        matched = []
        unmatched = []
        if environments:
            for item in items:
                if item.environmentgroups.match(environments):
                    matched.append(item)
                else:
                    unmatched.append(item)
        else:
            matched = items
        context[varname] = {"matched": matched, "unmatched": unmatched}
        return u""


register.tag(MatchEnvironment)
