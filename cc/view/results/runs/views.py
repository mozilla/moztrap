"""
Results views for runs.

"""
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from cc.view.utils.auth import login_maybe_required

from cc import model

from cc.view.filters import RunFilterSet
from cc.view.lists import decorators as lists
from cc.view.utils.ajax import ajax

from ..finders import ResultsFinder



@login_maybe_required
@lists.finder(ResultsFinder)
@lists.filter("runs", filterset_class=RunFilterSet)
@lists.sort("runs", "start", "asc")
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
        model.Run, pk=run_id)
    return TemplateResponse(
        request,
        "results/run/list/_run_details.html",
        {
            "run": run
            }
        )
