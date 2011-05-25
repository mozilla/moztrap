from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

from ..environments.forms import EnvironmentSelectionForm
from ..environments.util import set_environment_url
from ..products.models import ProductList
from ..static.status import TestRunStatus, TestCycleStatus
from ..users.decorators import login_required

from .models import TestCycleList, TestRun, TestRunList, TestResult



@login_required
def picker(request):
    products = ProductList.ours(auth=request.auth).sort("name", "asc")
    return TemplateResponse(
        request,
        "runtests/picker.html",
        {
            "products": products,
            "picker_type": "runtests",
            })



@login_required
def picker_cycles(request, parent_id):
    cycles = TestCycleList.get(auth=request.auth).filter(
        product=parent_id, status=TestCycleStatus.ACTIVE).sort("name", "asc")
    return TemplateResponse(
        request,
        "runtests/picker/_cycles.html",
        {
            "cycles": cycles,
            "picker_type": "runtests",
            })



@login_required
def picker_runs(request, parent_id):
    runs = TestRunList.get(auth=request.auth).filter(
        testCycle=parent_id, status=TestRunStatus.ACTIVE).sort("name", "asc")
    return TemplateResponse(
        request,
        "runtests/picker/_runs.html",
        {
            "runs": runs,
            "picker_type": "runtests",
            })



@login_required
def picker_environments(request, parent_id):
    run = TestRunList.get_by_id(parent_id, auth=request.auth)

    form = EnvironmentSelectionForm(
        groups=run.environmentgroups,
        current=request.session.get("environments", None))

    return TemplateResponse(
        request,
        "runtests/_environment_form.html",
        {"form": form,
         "action": set_environment_url(run.environmentgroups),
         "next": reverse("runtests_run", kwargs={"testrun_id": parent_id}),
         })



@login_required
def runtests(request, testrun_id):
    testrun = TestRun.get("testruns/%s" % testrun_id, auth=request.auth)

    if not testrun.environmentgroups.match(request.environments):
        return HttpResponseRedirect("%s&next=%s" % (
            set_environment_url(testrun.environmentgroups),
            request.path
            ))

    cycle = testrun.testCycle
    product = cycle.product

    return TemplateResponse(
        request,
        "runtests/run.html",
        {"product": product,
         "cycle": cycle,
         "testrun": testrun,
         "environmentgroups": testrun.environmentgroups,
         })



ACTIONS = {
    "start": [],
    "finishsucceed": [],
    "finishinvalidate": ["comment"],
    "finishfail": ["failedStepNumber", "actualResult"],
    }


@login_required
@require_POST
def result(request, result_id):
    result = TestResult.get(
        "testruns/results/%s" % result_id,
        auth=request.auth)

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
