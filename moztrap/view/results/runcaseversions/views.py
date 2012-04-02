"""
Results views for runcaseversions.

"""
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from cc.view.utils.auth import login_maybe_required

from cc import model

from cc.view.filters import RunCaseVersionFilterSet
from cc.view.lists import decorators as lists
from cc.view.utils.ajax import ajax

from ..finders import ResultsFinder



@login_maybe_required
@lists.finder(ResultsFinder)
@lists.filter("runcaseversions", filterset_class=RunCaseVersionFilterSet)
@lists.sort("runcaseversions")
@ajax("results/case/list/_cases_list.html")
def runcaseversions_list(request):
    """List runcaseversions."""
    return TemplateResponse(
        request,
        "results/case/cases.html",
        {
            "runcaseversions": model.RunCaseVersion.objects.select_related(),
            }
        )



@login_maybe_required
def runcaseversion_details(request, rcv_id):
    """Get details snippet for a runcaseversion."""
    runcaseversion = get_object_or_404(
        model.RunCaseVersion, pk=rcv_id)
    return TemplateResponse(
        request,
        "results/case/list/_case_details.html",
        {
            "runcaseversion": runcaseversion
            }
        )
