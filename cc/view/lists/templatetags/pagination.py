# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
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
"""
Template tags for pagination.

"""
from django.template import Library

from classytags.core import Tag, Options
from classytags.arguments import Argument

from .. import pagination



register = Library()



class Paginate(Tag):
    name = "paginate"
    options = Options(
        Argument("queryset"),
        "as",
        Argument("varname", resolve=False),
        )


    def render_tag(self, context, queryset, varname):
        request = context["request"]
        pagesize, pagenum = pagination.from_request(request)
        context[varname] = pagination.Pager(queryset, pagesize, pagenum)
        return u""


register.tag(Paginate)



@register.filter
def pagenumber_url(request, pagenumber):
    return pagination.pagenumber_url(request.get_full_path(), pagenumber)



@register.filter
def pagesize_url(request, pagesize):
    return pagination.pagesize_url(request.get_full_path(), pagesize)
