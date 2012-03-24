"""
Results views for runcaseversions.

"""
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from cc.view.utils.auth import login_maybe_required

from cc import model

from cc.view.filters import ResultFilterSet
from cc.view.lists import decorators as lists
from cc.view.utils.ajax import ajax

from ..finders import ResultsFinder



@login_maybe_required
@lists.finder(ResultsFinder)
@lists.filter("results", filterset_class=ResultFilterSet)
@lists.sort("results")
@ajax("results/result/list/_results_list.html")
def results_list(request, rcv_id):
    """List results for a given runcaseversion."""
    rcv = get_object_or_404(model.RunCaseVersion, pk=rcv_id)
    return TemplateResponse(
        request,
        "results/result/results.html",
        {
            "results": model.Result.objects.filter(
                runcaseversion=rcv).select_related(),
            "runcaseversion": rcv,
            }
        )
