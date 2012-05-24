"""
Finder for results pages.

"""
from django.core.urlresolvers import reverse

from ... import model
from ..lists import finder



class CaseColumn(finder.Column):
    """Finder column for case results; goto is to case-results-list."""
    def goto_url(self, obj):
        """Given an object, return its "Goto" url, or None."""
        if self.goto:
            return reverse(self.goto, kwargs={"rcv_id": obj.id})

        return None



class ResultsFinder(finder.Finder):
    template_base = "results/finder"

    columns = [
        finder.Column(
            "products",
            "_products.html",
            model.Product.objects.order_by("name"),
            ),
        finder.Column(
            "productversions",
            "_productversions.html",
            model.ProductVersion.objects.all(),
            "results_runs",
            ),
        finder.Column(
            "runs",
            "_runs.html",
            model.Run.objects.order_by("start"),
            "results_runcaseversions",
            ),
        CaseColumn(
            "cases",
            "_cases.html",
            model.RunCaseVersion.objects.order_by("caseversion__name"),
            "results_results",
            ),
        ]
