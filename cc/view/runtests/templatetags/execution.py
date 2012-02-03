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
"""Template tags/filters for running tests."""
from django import template

from .... import model



register = template.Library()



@register.simple_tag(takes_context=True)
def result_for(context, runcaseversion, user, environment, as_, name):
    """
    Sets Result for this runcaseversion/user/env in context under "name".

    If no relevant Result exists, returns *unsaved* default Result for use in
    template (result will be saved when case is started.)

    """
    result_kwargs = dict(
        # we can assume this is set, else the view will redirect
        environment=environment,
        tester=user,
        runcaseversion=runcaseversion
        )
    try:
        result = model.Result.get(**result_kwargs)
    except model.Result.DoesNotExist:
        result = model.Result(**result_kwargs)

    context[name] = result
