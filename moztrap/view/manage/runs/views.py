"""
Manage views for runs.

"""
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache

from django.contrib import messages

from moztrap import model
from moztrap.model.mtmodel import NotDeletedCount

from moztrap.view.filters import RunFilterSet
from moztrap.view.lists import decorators as lists
from moztrap.view.lists.filters import PinnedFilters
from moztrap.view.users.decorators import permission_required
from moztrap.view.utils.ajax import ajax
from moztrap.view.utils.auth import login_maybe_required

from ..finders import ManageFinder

from . import forms



@never_cache
@login_maybe_required
@lists.actions(
    model.Run,
    ["delete", "clone", "activate", "draft", "deactivate", "refresh"],
    permission="execution.manage_runs")
@lists.finder(ManageFinder)
@lists.filter("runs", filterset_class=RunFilterSet)
@lists.sort("runs")
@ajax("manage/run/list/_runs_list.html")
def runs_list(request):
    """List runs."""
    return TemplateResponse(
        request,
        "manage/run/runs.html",
        {
            "runs": model.Run.objects.select_related().annotate(
                suite_count=NotDeletedCount("suites", distinct=True)),
            }
        )



@never_cache
@login_maybe_required
def run_details(request, run_id):
    """Get details snippet for a run."""
    run = get_object_or_404(
        model.Run, pk=run_id)
    return TemplateResponse(
        request,
        "manage/run/list/_run_details.html",
        {
            "run": run
            }
        )



@never_cache
@permission_required("execution.manage_runs")
def run_add(request):
    """Add a run."""
    if request.method == "POST":
        form = forms.AddRunForm(request.POST, user=request.user)
        run = form.save_if_valid()
        if run is not None:
            messages.success(
                request, u"Run '{0}' added.".format(
                    run.name)
                )
            return redirect("manage_runs")
    else:
        pf = PinnedFilters(request.COOKIES)
        form = forms.AddRunForm(
            user=request.user,
            initial=pf.fill_form_querystring(request.GET).dict(),
            )
    return TemplateResponse(
        request,
        "manage/run/add_run.html",
        {
            "form": form
            }
        )



@never_cache
@permission_required("execution.manage_runs")
def run_edit(request, run_id):
    """Edit a run."""
    run = get_object_or_404(
        model.Run, pk=run_id)
    if request.method == "POST":
        form = forms.EditRunForm(
            request.POST, instance=run, user=request.user)
        saved_run = form.save_if_valid()
        if saved_run is not None:
            messages.success(request, u"Saved '{0}'.".format(saved_run.name))
            pre_page = request.GET.get('from', "manage_runs")
            return redirect(pre_page)
    else:
        form = forms.EditRunForm(
            instance=run, user=request.user)
    return TemplateResponse(
        request,
        "manage/run/edit_run.html",
        {
            "form": form,
            "run": run,
            }
        )
