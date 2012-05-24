"""
Views for test execution.

"""
import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache

from django.contrib import messages

from ... import model

from ..filters import RunTestsRunCaseVersionFilterSet
from ..lists import decorators as lists
from ..users.decorators import permission_required
from ..utils.ajax import ajax

from .finders import RunTestsFinder
from .forms import EnvironmentSelectionForm




@never_cache
@permission_required("execution.execute")
@lists.finder(RunTestsFinder)
def select(request):
    """Select an active test run to execute tests from."""
    return TemplateResponse(
        request,
        "runtests/select.html",
        {}
        )



@never_cache
@permission_required("execution.execute")
@ajax("runtests/_environment_form.html")
def set_environment(request, run_id):
    """Select valid environment for given run and save it in session."""
    run = get_object_or_404(model.Run, pk=run_id)

    try:
        current = int(request.GET.get("environment", None))
    except (TypeError, ValueError):
        current = None

    form_kwargs = {
        "current": current,
        "environments": run.environments.all()
        }

    if request.method == "POST":
        form = EnvironmentSelectionForm(
            request.POST,
            **form_kwargs)

        if form.is_valid():
            envid = form.save()
            return redirect("runtests_run", run_id=run_id, env_id=envid)
    else:
        form = EnvironmentSelectionForm(**form_kwargs)

    return TemplateResponse(
        request,
        "runtests/environment.html",
        {
            "envform": form,
            "run": run,
            }
        )



# maps valid action names to default parameters
ACTIONS = {
    "start": {},
    "finishsucceed": {},
    "finishinvalidate": {"comment": ""},
    "finishfail": {"stepnumber": None, "comment": "", "bug": ""},
    "restart": {},
    }



@never_cache
@permission_required("execution.execute")
@lists.finder(RunTestsFinder)
@lists.filter("runcaseversions", filterset_class=RunTestsRunCaseVersionFilterSet)
@lists.sort("runcaseversions")
@ajax("runtests/list/_runtest_list.html")
def run(request, run_id, env_id):
    run = get_object_or_404(model.Run.objects.select_related(), pk=run_id)

    if not run.status == model.Run.STATUS.active:
        messages.info(
            request,
            "That test run is currently not open for testing. "
            "Please select a different test run.")
        return redirect("runtests")

    try:
        environment = run.environments.get(pk=env_id)
    except model.Environment.DoesNotExist:
        return redirect("runtests_environment", run_id=run_id)

    if request.method == "POST":
        prefix = "action-"
        while True:
            rcv = None

            try:
                action, rcv_id = [
                    (k[len(prefix):], int(v)) for k, v in request.POST.items()
                    if k.startswith(prefix)
                    ][0]
            except IndexError:
                break

            try:
                defaults = ACTIONS[action].copy()
            except KeyError:
                messages.error(
                    request, "{0} is not a valid action.".format(action))
                break

            try:
                rcv = run.runcaseversions.get(pk=rcv_id)
            except model.RunCaseVersion.DoesNotExist:
                messages.error(
                    request,
                    "{0} is not a valid run/caseversion ID.".format(rcv_id))
                break

            try:
                result = rcv.results.get(
                    tester=request.user, environment=environment)
            except model.Result.DoesNotExist:
                result = model.Result.objects.create(
                    runcaseversion=rcv,
                    tester=request.user,
                    environment=environment,
                    user=request.user)

            for argname in defaults.keys():
                try:
                    defaults[argname] = request.POST[argname]
                except KeyError:
                    pass

            getattr(result, action)(**defaults)
            break

        if request.is_ajax():
            # if we don't know the runcaseversion id, we return an empty
            # response.
            if rcv is None:
                return HttpResponse(
                    json.dumps({"html": "", "no_replace": True}),
                    content_type = "application/json",
                    )
            # by not returning a TemplateResponse, we skip the sort and finder
            # decorators, which aren't applicable to a single case.
            return render(
                request,
                "runtests/list/_runtest_list_item.html",
                {
                    "environment": environment,
                    "runcaseversion": rcv
                    }
                )
        else:
            return redirect(request.get_full_path())

    envform = EnvironmentSelectionForm(
        current=environment.id, environments=run.environments.all())


    return TemplateResponse(
        request,
        "runtests/run.html",
        {
            "environment": environment,
            "product": run.productversion.product,
            "productversion": run.productversion,
            "run": run,
            "envform": envform,
            "runcaseversions": run.runcaseversions.select_related(
                "caseversion").filter(environments=environment),
            "finder": {
                # finder decorator populates top column (products), we
                # prepopulate the other two columns
                "productversions": model.ProductVersion.objects.filter(
                    product=run.productversion.product),
                "runs": model.Run.objects.order_by("name").filter(
                    productversion=run.productversion,
                    status=model.Run.STATUS.active),
                },
            }
        )
