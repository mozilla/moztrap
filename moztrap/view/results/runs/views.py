"""
Results views for runs.

"""
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from moztrap.view.utils.auth import login_maybe_required

from moztrap import model

from moztrap.view.filters import RunFilterSet
from moztrap.view.lists import decorators as lists
from moztrap.view.utils.ajax import ajax

from ..finders import ResultsFinder



@login_maybe_required
@lists.finder(ResultsFinder)
@lists.filter("runs", filterset_class=RunFilterSet)
@lists.sort("runs", "start", "desc")
@ajax("results/run/list/_runs_list.html")
def runs_list(request):
    """List runs."""
    return TemplateResponse(
        request,
        "results/run/runs.html",
        {
            "runs": model.Run.objects.select_related(),
            }
        )



@login_maybe_required
def run_details(request, run_id):
    """Get details snippet for a run."""
    run = get_object_or_404(
        model.Run.objects.prefetch_related(
            "environments",
            "environments__elements"), pk=run_id)
    return TemplateResponse(
        request,
        "results/run/list/_run_details.html",
        {
            "run": run
            }
        )
