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

from classytags.core import Tag, Options
from classytags.arguments import Argument

from .... import model



register = template.Library()



class ResultFor(Tag):
    """
    Places Result for this runcaseversion/user/env in context.

    If no relevant Result exists, returns *unsaved* default Result for use in
    template (result will be saved when case is started.)

    """
    name = "result_for"
    options = Options(
        Argument("runcaseversion"),
        Argument("user"),
        Argument("environment"),
        "as",
        Argument("varname", resolve=False),
        )


    def render_tag(self, context, runcaseversion, user, environment, varname):
        """Get/construct Result and place it in context under ``varname``"""
        result_kwargs = dict(
            environment=environment,
            tester=user,
            runcaseversion=runcaseversion
            )
        try:
            result = model.Result.objects.get(**result_kwargs)
        except model.Result.DoesNotExist:
            result = model.Result(**result_kwargs)
        except model.Result.MultipleObjectsReturned:
            dupes = model.Result.objects.filter(**result_kwargs).order_by(
                "-modified_on")
            incomplete_states = set(
                [model.Result.STATUS.assigned, model.Result.STATUS.started])
            # prioritize keeping completed results
            candidates = [r for r in dupes if r.status not in incomplete_states]
            if not candidates:
                candidates = list(dupes)
            # keep the last-modified result of the prioritized set
            result = candidates[0]
            model.Result.objects.filter(
                **result_kwargs).exclude(pk=result.pk).delete()

        context[varname] = result
        return u""


register.tag(ResultFor)



class StepResultFor(Tag):
    """
    Places StepResult for this result/casestep in context.

    If no relevant StepResult exists, returns *unsaved* default StepResult for
    use in template.

    """
    name = "stepresult_for"
    options = Options(
        Argument("result"),
        Argument("casestep"),
        "as",
        Argument("varname", resolve=False),
        )


    def render_tag(self, context, result, casestep, varname):
        """Get/construct StepResult and place it in context under ``varname``"""
        stepresult_kwargs = dict(
            result=result,
            step=casestep,
            )
        try:
            stepresult = model.StepResult.objects.get(**stepresult_kwargs)
        except model.StepResult.DoesNotExist:
            stepresult = model.StepResult(**stepresult_kwargs)

        context[varname] = stepresult
        return u""


register.tag(StepResultFor)
