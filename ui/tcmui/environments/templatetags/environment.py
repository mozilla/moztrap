from django import template

from classytags.core import Tag, Options
from classytags.arguments import Argument

from ..forms import EnvironmentSelectionForm



register = template.Library()



class GetEnvironmentSelectionForm(Tag):
    name = "get_environment_selection_form"
    options = Options(
        "for",
        Argument("product"),
        "as",
        Argument("varname", resolve=False)
        )


    def render_tag(self, context, product, varname):
        context[varname] = EnvironmentSelectionForm(
            groups=product.environmentgroups)
        return u""



register.tag(GetEnvironmentSelectionForm)
