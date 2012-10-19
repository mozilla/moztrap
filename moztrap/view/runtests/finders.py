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
                series=None,
                ),
            ),
        ]


    def child_query_url(self, obj):
        if isinstance(obj, model.Run):
            return reverse("runtests_environment", kwargs={"run_id": obj.id})
        return super(RunTestsFinder, self).child_query_url(obj)
