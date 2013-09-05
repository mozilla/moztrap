"""
Results views for runcaseversions.

"""
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from moztrap.view.utils.auth import login_maybe_required

from moztrap import model

from moztrap.view.filters import RunCaseVersionFilterSet
from moztrap.view.lists import decorators as lists
from moztrap.view.utils.ajax import ajax

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
            # "runcaseversions": model.RunCaseVersion.objects.select_related(),
            "runcaseversions": model.RunCaseVersion.objects.only(
                "caseversion__name",
                "caseversion__case__priority",
                "run__name",
                "run__productversion",
                "run__productversion__version",
                "run__productversion__product__name",
                ).select_related(
                    "results",
                    "run",
                    "run__productversion",
                    "run__productversion__product",
                    "caseversion__case__priority",
                    )#.prefetch_related("environments"),
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
