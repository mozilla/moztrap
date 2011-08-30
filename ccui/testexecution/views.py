from django.shortcuts import render_to_response, redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from ..core import decorators as dec
from ..static.status import TestRunStatus, TestCycleStatus
from ..users.decorators import login_redirect

from .finder import RunTestsFinder
from .models import TestCycleList, TestRunList, TestResultList



@login_redirect
@dec.finder(RunTestsFinder)
def home(request):
    return TemplateResponse(
        request,
        "runtests/home.html",
        {}
        )



@login_redirect
def finder_environments(request, run_id):
    run = TestRunList.get_by_id(run_id, auth=request.auth)

    return TemplateResponse(
        request,
        "runtests/_environment_form.html",
        {"testrun": run,
         })



@never_cache
@login_redirect
@dec.finder(RunTestsFinder)
def runtests(request, testrun_id):
    testrun = TestRunList.get_by_id(testrun_id, auth=request.auth)

    if not testrun.environmentgroups_prefetch.match(request.environments):
        return redirect("runtests_environment", testrun_id=testrun_id)

    cycle = testrun.testCycle
    product = cycle.product

    # for prepopulating finder
    cycles = TestCycleList.ours(auth=request.auth).sort("name", "asc").filter(
        product=product, status=TestCycleStatus.ACTIVE)
    runs = TestRunList.ours(auth=request.auth).sort("name", "asc").filter(
        testCycle=cycle, status=TestRunStatus.ACTIVE)

    return TemplateResponse(
        request,
        "runtests/run.html",
        {"product": product,
         "cycle": cycle,
         "testrun": testrun,
         "finder": {
                "cycles": cycles,
                "runs": runs,
                },
         })



ACTIONS = {
    "start": [],
    "finishsucceed": [],
    "finishinvalidate": ["comment"],
    "finishfail": ["failedStepNumber", "actualResult"],
    }


@login_redirect
@require_POST
def result(request, result_id):
    result = TestResultList.get_by_id(result_id, auth=request.auth)

    action = request.POST.get("action", None)
    try:
        argnames = ACTIONS[action]
    except KeyError:
        return HttpResponseBadRequest(
            "%s is not a valid result action." % action)

    kwargs = {"auth": request.auth}

    for argname in argnames:
        try:
            kwargs[argname] = request.POST[argname]
        except KeyError:
            return HttpResponseBadRequest(
                "Required parameter %s missing." % argname)

    getattr(result, action)(**kwargs)

    return render_to_response(
        "runtests/_run_case.html",
        {"case": result.testCase,
         "caseversion": result.testCaseVersion,
         "result": result,
         "open": action == "start",
         })
