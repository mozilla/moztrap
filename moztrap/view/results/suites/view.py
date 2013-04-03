"""
Results views for suites.

"""
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from moztrap.view.utils.auth import login_maybe_required

from moztrap import model

from moztrap.view.filters import SuiteFilterSet
from moztrap.view.lists import decorators as lists
from moztrap.view.utils.ajax import ajax

from ..finders import ResultsFinder



@login_maybe_required
@lists.finder(ResultsFinder)
@lists.filter("suites", filterset_class=SuiteFilterSet)
@lists.sort("suites", "start", "desc")
@ajax("results/suite/list/_suite_list.html")
def suites_list(request):
    """List suites."""
    return TemplateResponse(
        request,
        "results/suite/suites.html",
        {
            "suites": model.Suite.objects.select_related(),
        }
    )



@login_maybe_required
def suite_details(request, suite_id):
    """Get details snippet for a suite."""
    suite = get_object_or_404(
        model.Suite.objects.prefetch_related(), pk=suite_id)
    return TemplateResponse(
        request,
        "results/suite/list/_suite_details.html",
        {
            "suite": suite
        }
    )
