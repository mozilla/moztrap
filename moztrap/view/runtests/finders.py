"""
Finder for running tests.

"""
from django.core.urlresolvers import reverse

from ... import model
from ..lists import finder



class RunTestsFinder(finder.Finder):
    template_base = "runtests/finder"

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
            ),
        finder.Column(
            "runs",
            "_runs.html",
            model.Run.objects.filter(
                status=model.Run.STATUS.active,
                # only show stand-alone runs or runs that are a series.
                # don't show runs that are individual members of a series.
                # to run a member of a series, run the series, then specify
                # the build id that has an existing series member for it.
                # Having the series members here would be noisy and confusing.
                series=None,
                ),
            ),
        ]


    def child_query_url(self, obj):
        if isinstance(obj, model.Run):
            return reverse("runtests_environment", kwargs={"run_id": obj.id})
        return super(RunTestsFinder, self).child_query_url(obj)
