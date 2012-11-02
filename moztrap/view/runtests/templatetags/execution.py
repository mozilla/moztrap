"""Template tags/filters for running tests."""
from django import template

from classytags.core import Tag, Options
from classytags.arguments import Argument

from .... import model



register = template.Library()


def get_result(runcaseversion, user, environment):
    result_kwargs = dict(
        environment=environment,
        tester=user,
        runcaseversion=runcaseversion,
        is_latest=True,
        )
    try:
        result = model.Result.objects.get(**result_kwargs)
    except model.Result.DoesNotExist:
        result = model.Result(**result_kwargs)
    except model.Result.MultipleObjectsReturned:
        # find the latest one and set it to latest, which will set all
        # others to is_latest=False
        result = model.Result.objects.filter(**result_kwargs).order_by(
            "-modified_on")[0]
        result.set_latest()
        result.save()
    return result


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
#        result_kwargs = dict(
#            environment=environment,
#            tester=user,
#            runcaseversion=runcaseversion,
#            is_latest=True,
#            )
#        try:
#            result = model.Result.objects.get(**result_kwargs)
#        except model.Result.DoesNotExist:
#            result = model.Result(**result_kwargs)
#        except model.Result.MultipleObjectsReturned:
#            # find the latest one and set it to latest, which will set all
#            # others to is_latest=False
#            result = model.Result.objects.filter(**result_kwargs).order_by(
#                "-modified_on")[0]
#            result.set_latest()
#            result.save()

        context[varname] = get_result(runcaseversion, user, environment)
        return u""


register.tag(ResultFor)



class SummaryResultFor(Tag):
    """
    Places Result for this runcaseversion/user/env in context.

    If no relevant Result exists, returns *unsaved* default Result for use in
    template (result will be saved when case is started.)

    """
    name = "summary_result_for"
    options = Options(
        Argument("runcaseversion"),
        Argument("user"),
        Argument("environment"),
        "as",
        Argument("varname", resolve=False),
        "and",
        Argument("summary_varname", resolve=False)
        )


    def render_tag(self, context, runcaseversion, user, environment, varname,
                   summary_varname):
        """Get/construct Result and place it in context under ``varname``"""

        result =  get_result(runcaseversion, user, environment)
        context[varname] = result

        summary_result = result

        # if the result.status is pending or assigned, then we try to find a result
        # from another user to return instead.
        if result.status == result.STATUS.assigned or result.status == result.STATUS.started:
            include_kwargs = dict(
                environment=environment,
                runcaseversion=runcaseversion,
                is_latest=True,
                )
            exclude_kwargs = dict(
                tester=user,
                )

            try:
                summary_result = model.Result.objects.filter(
                    **include_kwargs).exclude(**exclude_kwargs).order_by(
                    "-modified_on")[0]
            except IndexError:
                pass


        context[summary_varname] = summary_result
        return u""


register.tag(SummaryResultFor)



class ResultTitle(Tag):
    """
    Returns the title test that should show over the displayed result

    Depends if there is no result yet, or if its not tested by user
    and IS tested by another user

    """
    name = "result_title"
    options = Options(
        Argument("result"),
        Argument("user"),
        "as",
        Argument("varname", resolve=False),
        )


    def render_tag(self, context, result, user, varname):
        """Get/construct text and place it in context under ``varname``"""

        if result.status == result.STATUS.assigned or result.status == result.STATUS.started:
            context[varname] = "not yet tested"
        elif result.tester == user:
            context[varname] = "{0} by you".format(result.status)
        else:
            context[varname] = "{0} by {1} - click to submit your own result".format(result.status, result.tester)
        return u""


register.tag(ResultTitle)



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
