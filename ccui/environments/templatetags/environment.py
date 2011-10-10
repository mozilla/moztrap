# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
# 
# This file is part of Case Conductor.
# 
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
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
